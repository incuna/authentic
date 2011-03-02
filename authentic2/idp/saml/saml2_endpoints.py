import datetime
import logging

import lasso
from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import *
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.contenttypes.models import ContentType

import authentic2.idp as idp
import authentic2.idp.views as idp_views
from authentic2.saml.models import *
from authentic2.saml.common import *
import authentic2.saml.saml2utils as saml2utils
from authentic2.auth2_auth.models import AuthenticationEvent
from common import redirect_to_login, kill_django_sessions
from authentic2.auth2_auth import NONCE_FIELD_NAME
from authentic2.idp.interactions import consent_federation, consent_attributes

from authentic2.idp import signals as idp_signals
from authentic2.idp.models import *

'''SAMLv2 IdP implementation

   It contains endpoints to receive:
    - authentication requests,
    - logout request,
    - logout response,
    - name id management requests,
    - name id management responses,
    - attribut requests.

    TODO:
     - logout
     - logoutResponse
     - manageNameId
     - manageNameIdResponse
     - assertionIDRequest
'''

logger = logging.getLogger('authentic2.idp.saml')

metadata_map = (
        (saml2utils.Saml2Metadata.SINGLE_SIGN_ON_SERVICE, asynchronous_bindings , '/sso'),
        (saml2utils.Saml2Metadata.SINGLE_LOGOUT_SERVICE, asynchronous_bindings, '/slo', '/slo_return'),
        (saml2utils.Saml2Metadata.SINGLE_LOGOUT_SERVICE, soap_bindings, '/slo/soap'),
        (saml2utils.Saml2Metadata.ARTIFACT_RESOLUTION_SERVICE, lasso.SAML2_METADATA_BINDING_SOAP, '/artifact')
)
metadata_options = { 'key': settings.SAML_SIGNING_KEY }

def metadata(request):
    '''Endpoint to retrieve the metadata file'''
    logger.info('metadata: return metadata')
    return HttpResponse(get_metadata(request, request.path),
            mimetype='text/xml')

#####
# SSO
#####
def register_new_saml2_session(request, login, federation=None):
    '''Persist the newly created session for emitted assertion'''
    logger.info("register_new_saml2_session: assertion and saml session registration")
    lib_assertion = LibertyAssertion(saml2_assertion=login.assertion)
    lib_assertion.save()
    logger.debug('register_new_saml2_session: assertion saved')
    lib_session = LibertySession(provider_id=login.remoteProviderId,
            saml2_assertion=login.assertion, federation=federation,
            django_session_key=request.session.session_key,
            assertion=lib_assertion)
    lib_session.save()
    logger.debug('register_new_saml2_session: session saved')

def fill_assertion(request, saml_request, assertion, provider_id, nid_format):
    '''Stuff an assertion with information extracted from the user record
       and from the session, and eventually from transactions linked to the
       request, i.e. a login event or a consent event.

       No check on the request must be done here, the sso method should have
       verified that the request can be answered and match any policy for the
       given provider or modified the request to match the identity provider
       policy.

    TODO: add attributes from user account
    TODO: determine and add attributes from the session, for anonymous users
    (pseudonymous federation, openid without accounts)
    # TODO: add information from the login event, of the session or linked
    # to the request id
    # TODO: use information from the consent event to specialize release of
    # attributes (user only authorized to give its email for email)
       '''
    logger.info('fill_assertion: fill assertion with the nameid format %s' %nid_format)
    # Use assertion ID as session index
    assertion.authnStatement[0].sessionIndex = assertion.id
    logger.debug('fill_assertion: assertion.authnStatement[0].sessionIndex = %s' %assertion.id)
    # NameID
    if nid_format in ('persistent', 'transient'):
        logger.debug("fill_assertion: nid_format in ('persistent', 'transient')")
        pass
    elif nid_format == 'email':
        logger.debug("fill_assertion: nid_format is email")
        assertion.subject.nameID.content = request.user.email
    else:
        # It should not happen as the nid_format has been checked
        # before
        logger.error("fill_assertion: unsupported nid_format %s" %nid_format)
        assert False

def saml2_add_attribute_values(assertion, attributes):
    if not attributes:
        logger.info("saml2_add_attribute_values: there are no attributes to add")
    else:
        logger.info("saml2_add_attribute_values: there are attributes to add")
        logger.debug("saml2_add_attribute_values: assertion before processing %s" %assertion.dump())
        logger.debug("saml2_add_attribute_values: adding attributes %s" %str(attributes))
        if not assertion.attributeStatement:
            assertion.attributeStatement = [ lasso.Saml2AttributeStatement() ]
        attribute_statement = assertion.attributeStatement[0]
        for key in attributes.keys():
            attribute = lasso.Saml2Attribute()
            # Only name/values or name/format/values
            name = None
            values = None
            if type(key) is tuple and len(key) == 2:
                name, format = key
                attribute.nameFormat = format
                values = attributes[(name, format)]
            elif type(key) is tuple:
                return
            else:
                name = key
                attribute.nameFormat = lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC
                values = attributes[key]
            attribute.name = name
            attribute_statement.attribute = list(attribute_statement.attribute) + [ attribute ]
            attribute_value_list = list(attribute.attributeValue)
            for value in values:
                if value is True:
                    value = 'true'
                elif value is False:
                    value = 'false'
                else:
                    value = str(value)
                if type(value) is unicode:
                    value = value.encode('utf-8')
                #else:
                #    value = sitecharset2utf8(value)
                text_node = lasso.MiscTextNode.newWithString(value)
                text_node.textChild = True
                attribute_value = lasso.Saml2AttributeValue()
                attribute_value.any = [ text_node ]
                attribute_value_list.append(attribute_value)
            attribute.attributeValue = attribute_value_list
        logger.debug("saml2_add_attribute_values: assertion after processing %s" %assertion.dump())

def build_assertion(request, login, nid_format = 'transient', attributes=None):
    '''After a successfully validated authentication request, build an
       authentication assertion'''
    now = datetime.datetime.utcnow()
    logger.info("build_assertion: building assertion at %s" %str(now))
    # 1 minute ago
    notBefore = now-datetime.timedelta(0,__delta)
    # 1 minute in the future
    notOnOrAfter = now+datetime.timedelta(0,__delta)
    ssl = request.environ.has_key('HTTPS')
    if __user_backend_from_session:
        backend = request.session[BACKEND_SESSION_KEY]
        logger.debug("build_assertion: backend from session %s" %backend)
        if backend in ('django.contrib.auth.backends.ModelBackend',
                'authentic2.idp.auth_backends.LogginBackend',
                'django_auth_ldap.backend.LDAPBackend'):
            if ssl:
                authn_context = lasso.SAML2_AUTHN_CONTEXT_PASSWORD_PROTECTED_TRANSPORT
            else:
                authn_context = lasso.SAML2_AUTHN_CONTEXT_PASSWORD
        elif backend == 'authentic2.sslauth.backends.SSLAuthBackend':
            authn_context = lasso.SAML2_AUTHN_CONTEXT_X509
        # XXX: grab context from the assertion received
        elif backend == 'authentic2.authsaml2.backends.AuthSAML2PersistentBackend':
            authn_context = lasso.SAML2_AUTHN_CONTEXT_UNSPECIFIED
        elif backend == 'authentic2.authsaml2.backends.AuthSAML2TransientBackend':
            authn_context = lasso.SAML2_AUTHN_CONTEXT_UNSPECIFIED
        else:
            raise Exception('unknown backend: ' + backend)
    else:
        logger.debug("build_assertion: backend from stored event %s" %sbackend)
        try:
            auth_event = AuthenticationEvent.objects.get(nonce = login.request.id)
            if auth_event.how == 'password':
                authn_context = lasso.SAML2_AUTHN_CONTEXT_PASSWORD
            elif auth_event.how == 'password-on-https':
                authn_context = lasso.SAML2_AUTHN_CONTEXT_PASSWORD_PROTECTED_TRANSPORT
            elif auth_event.how == 'ssl':
                authn_context = lasso.SAML2_AUTHN_CONTEXT_X509
            else:
                raise NotImplementedError('Unknown authentication method %r' % auth_event.how)
        except ObjectDoesNotExist:
            logger.debug("build_assertion: backend from stored event not found %s" %backend)
            # TODO: previous session over secure transport (ssl) ?
            authn_context = lasso.SAML2_AUTHN_CONTEXT_PREVIOUS_SESSION
    logger.info("build_assertion: authn_context %s" %authn_context)
    login.buildAssertion(authn_context,
            now.isoformat()+'Z',
            'unused', # reauthenticateOnOrAfter is only for ID-FF 1.2
            notBefore.isoformat()+'Z',
            notOnOrAfter.isoformat()+'Z')
    assertion = login.assertion
    logger.debug("build_assertion: assertion building in progress %s" %assertion.dump())
    logger.debug("build_assertion: fill assertion")
    fill_assertion(request, login.request, assertion, login.remoteProviderId, nid_format)
    # Save federation and new session
    if login.assertion.subject.nameID.format == lasso.SAML2_NAME_IDENTIFIER_FORMAT_PERSISTENT:
        logger.debug("build_assertion: nameID persistent, get or create federation")
        kwargs = nameid2kwargs(login.assertion.subject.nameID)
        federation, new = LibertyFederation.objects.get_or_create(
                idp_id=login.server.providerId,
                sp_id=login.remoteProviderId,
                user=request.user, **kwargs)
        if new:
            logger.info("build_assertion: nameID persistent, new federation")
            federation.save()
        else:
            logger.info("build_assertion: nameID persistent, existing federation")
    else:
        logger.debug("build_assertion: nameID not persistent, no federation management")
        federation = None
    if attributes:
        logger.debug("build_assertion: add attributes to the assertion")
        saml2_add_attribute_values(login.assertion, attributes)
    register_new_saml2_session(request, login, federation=federation)

@csrf_exempt
def sso(request):
    """Endpoint for receiving saml2:AuthnRequests by POST, Redirect or SOAP.
       For SOAP a session must be established previously through the login page. No authentication through the SOAP request is supported.
    """
    logger.info("sso: performing sso")
    consent_answer = None
    if request.method == "GET":
        logger.debug('sso: called by GET')
        consent_answer = request.GET.get('consent_answer', '')
        if consent_answer:
            logger.info('sso: back from the consent page for federation with answer %s' %consent_answer)
    message = get_saml2_request_message(request)
    server = create_server(request)
    login = lasso.Login(server)
    # 1. Process the request, separate POST and GET treatment
    if not message:
        logger.warn("sso: missing query string")
        return HttpResponseForbidden('A SAMLv2 Single Sign On request need a query string')
    logger.debug('sso: processing sso request %r' % message)
    while True:
        try:
            login.processAuthnRequestMsg(message)
            break
        except (lasso.ProfileInvalidMsgError,
            lasso.ProfileMissingIssuerError,), e:
            logger.error('sss: invalid message for WebSSO profile with '
                          'HTTP-Redirect binding: %r exception: %s' % (message, e))
            return HttpResponseBadRequest(_('SAMLv2 Single Sign On: invalid message for '
                'WebSSO profile with HTTP-Redirect binding: %r') % message)
        except lasso.ProfileInvalidProtocolprofileError:
            log_info_authn_request_details(login)
            message = N_('SAMLv2 Single Sign On: the request cannot be answered because no valid protocol binding could be found')
            logger.error('sso: the request cannot be answered because no valid protocol binding could be found')
            return HttpResponseBadRequest(_(message))
        except lasso.DsError, e:
            log_info_authn_request_details(login)
            logger.error('sso: digital signature treatment error: %s' % e)
            return return_login_response(request, login)
        except (lasso.ServerProviderNotFoundError,
                lasso.ProfileUnknownProviderError):
            logger.debug('sso: processAuthnRequestMsg not successful')
            log_info_authn_request_details(login)
            provider_id = login.remoteProviderId
            logger.debug('sso: loading provider %s' %provider_id)
            provider_loaded = load_provider(request, provider_id,
                    server=login.server)
            if not provider_loaded:
                consent_obtained = False
                message = _('sso: fail to load unknown provider %s' %provider_id)
                return error_page(request, message)
            else:
                logger.info('sso: provider %s loaded with success' %provider_id)
                consent_obtained = \
                        not provider_loaded.service_provider.ask_user_consent
                logger.info('sso: the user consent option given by the requester is %s' %str(consent_obtained))
    if not check_destination(request, login.request):
        logger.error('sso: wrong or absent destination')
        return return_login_error(request, login,
                AUTHENTIC_STATUS_CODE_MISSING_DESTINATION)
    # Check NameIDPolicy or force the NameIDPolicy
    if consent_answer == 'refused':
        #XXX: Handle option to send transient to the SP
        logger.info('sso: consent answer treatment, the user refused, return request denied to the requester')
        set_saml2_response_responder_status_code(login.response,
                lasso.SAML2_STATUS_CODE_REQUEST_DENIED)
        return finish_sso(request, login)
    if consent_answer == 'accepted':
        logger.info('sso: consent answer treatment, the user accepted, continue')
        consent_obtained = True
    name_id_policy = login.request.nameIdPolicy
    logger.debug('sso: nameID policy is %s' %name_id_policy.dump())
    if name_id_policy.format and \
            name_id_policy.format != \
                lasso.SAML2_NAME_IDENTIFIER_FORMAT_UNSPECIFIED:
        nid_format = saml2_urn_to_nidformat(name_id_policy.format)
        logger.debug('sso: nameID format %s' %nid_format)
        default_nid_format = provider_loaded.service_provider.default_name_id_format
        logger.debug('sso: default nameID format %s' %default_nid_format)
        accepted_nid_format = \
                provider_loaded.service_provider.accepted_name_id_format
        logger.debug('sso: nameID format accepted %s' %str(accepted_nid_format))
        if (not nid_format or nid_format not in accepted_nid_format) and \
           default_nid_format != nid_format:
            set_saml2_response_responder_status_code(login.response,
                lasso.SAML2_STATUS_CODE_INVALID_NAME_ID_POLICY)
            logger.error('sso: NameID format required is not accepted')
            return finish_sso(request, login)
    else:
        logger.debug('sso: no nameID policy format')
        nid_format = provider_loaded.service_provider.default_name_id_format
        logger.debug('sso: set nameID policy format %s' %nid_format)
        name_id_policy.format = nidformat_to_saml2_urn(nid_format)
    return sso_after_process_request(request, login,
        consent_obtained = consent_obtained, nid_format = nid_format)

def need_login(request, login, consent_obtained, save, nid_format):
    '''Redirect to the login page with a nonce parameter to verify later that
       the login form was submitted'''
    nonce = login.request.id
    save_key_values(nonce, login.dump(), consent_obtained, save, nid_format)
    url = reverse(continue_sso)+'?%s=%s' % (NONCE_FIELD_NAME, nonce)
    logger.debug('need_login: redirect to login page with next url %s' %url)
    return redirect_to_login(url,
            other_keys={NONCE_FIELD_NAME: nonce})

def need_consent_for_federation(request, login, consent_obtained, save, nid_format):
    nonce = login.request.id
    save_key_values(nonce, login.dump(), consent_obtained, save, nid_format)
    url = '%s?%s=%s&next=%s&provider_id=%s' % (reverse(consent_federation), NONCE_FIELD_NAME,
        nonce, urllib.quote(request.get_full_path()), urllib.quote(login.request.issuer.content))
    logger.debug('need_consent_for_federation: redirect to url %s' %url)
    return HttpResponseRedirect(url)

def need_consent_for_attributes(request, login, consent_obtained, save, nid_format):
    nonce = login.request.id
    save_key_values(nonce, login.dump(), consent_obtained, save, nid_format)
    url = '%s?%s=%s&next=%s&provider_id=%s' % (reverse(consent_attributes), NONCE_FIELD_NAME,
        nonce, urllib.quote(request.get_full_path()), urllib.quote(login.request.issuer.content))
    logger.debug('need_consent_for_attributes: redirect to url %s' %url)
    return HttpResponseRedirect(url)

def continue_sso(request):
    consent_answer = None
    if request.method == "GET":
        logger.debug('continue_sso: called by GET')
        consent_answer = request.GET.get('consent_answer', '')
        if consent_answer:
            logger.info('continue_sso: back from the consent page for federation with answer %s' %consent_answer)
    nonce = request.REQUEST.get(NONCE_FIELD_NAME, '')
    if not nonce:
        logger.error('continue_sso: nonce not found')
        return HttpResponseBadRequest()
    login_dump, consent_obtained, save, nid_format = \
            get_and_delete_key_values(nonce)
    server = create_server(request)
    # XXX: The following function does not work!
    login = lasso.Login.newFromDump(server, login_dump)
    logger.debug('continue_sso: login newFromDump done')
    if not login:
        return error_page(request, _('continue_sso: error loading login'))
    if not load_provider(request, login.remoteProviderId, server=login.server):
        return error_page(request, _('continue_sso: unknown provider %s') %login.remoteProviderId)
    if consent_answer == 'refused':
        logger.info('continue_sso: consent answer treatment, the user refused, return request denied to the requester')
        set_saml2_response_responder_status_code(login.response,
                lasso.SAML2_STATUS_CODE_REQUEST_DENIED)
        return finish_sso(request, login)
    if consent_answer == 'accepted':
        logger.info('continue_sso: consent answer treatment, the user accepted, continue')
        consent_obtained = True
    return sso_after_process_request(request, login,
            consent_obtained = consent_obtained, nid_format = nid_format)

def sso_after_process_request(request, login,
        consent_obtained = True, user = None, save = True, nid_format = 'transient'):
    '''Common path for sso and idp_initiated_sso.

       consent_obtained: whether the user has given his consent to this federation
       user: the user which must be federated, if None, current user is the default.
       save: whether to save the result of this transaction or not.
    '''
    nonce = login.request.id
    user = user or request.user
    did_auth = AuthenticationEvent.objects.filter(nonce=nonce).exists()
    force_authn = login.request.forceAuthn
    passive = login.request.isPassive

    # TODO: If the sp ask for persistent, refuse login creting a transient

    # XXX: if not passive and (not user.is_authenticated() or (force_authn and not did_auth)):
    if not passive and (user.is_anonymous() or (force_authn and not did_auth)):
        logger.info('sso_after_process_request: login required')
        return need_login(request, login, consent_obtained, save, nid_format)

    # Transient user
    # If the SP asks for persistent, reject
    transient = False
    #if ContentType.objects.get_for_model(request.user) == 'SAML2TransientUser':
    if str(request.user.__class__).find('SAML2TransientUser') > -1:
        logger.debug('sso_after_process_request: the user is transient')
        transient = True
    if transient and login.request.nameIdPolicy.format == lasso.SAML2_NAME_IDENTIFIER_FORMAT_PERSISTENT:
        logger.info('sso_after_process_request: access denied, the user is transient and the sp ask for persistent')
        set_saml2_response_responder_status_code(login.response,
                lasso.SAML2_STATUS_CODE_REQUEST_DENIED)
        return finish_sso(request, login)
    # If the sp does not allow create, reject
    if transient and login.request.nameIdPolicy.allowCreate == 'false':
        logger.info('sso_after_process_request: access denied, we created a transient user and allow creation is not authorized by the SP')
        set_saml2_response_responder_status_code(login.response,
                lasso.SAML2_STATUS_CODE_REQUEST_DENIED)
        return finish_sso(request, login)

    decisions = idp_signals.authorize_service.send(sender=None,
         request=request, user=request.user, audience=login.remoteProviderId)
    logger.info('sso_after_process_request: signal authorize_service sent')

    # You don't dream. By default, access granted.
    # We catch denied decisions i.e. dic['authz'] = False
    access_granted = True
    for decision in decisions:
        logger.info('sso_after_process_request: authorize_service connected to function %s' % \
            decision[0].__name__)
        dic = decision[1]
        if dic and dic.has_key('authz'):
            logger.info('sso_after_process_request: decision is %s' %dic['authz'])
            if dic.has_key('message'):
                logger.info('sso_after_process_request: with message %s' %dic['message'])
            if not dic['authz']:
                logger.info('sso_after_process_request: access denied by an external function')
                access_granted = False
        else:
            logger.info('sso_after_process_request: no function connected to authorize_service')

    if not access_granted:
        logger.info('sso_after_process_request: access denied, return answer to the requester')
        set_saml2_response_responder_status_code(login.response,
                lasso.SAML2_STATUS_CODE_REQUEST_DENIED)
        return finish_sso(request, login)

    attributes_provided = idp_signals.add_attributes_to_response.send(sender=None,
         request=request, user=request.user, audience=login.remoteProviderId)
    logger.info('sso_after_process_request: signal add_attributes_to_response sent')

    attributes = {}
    for attrs in attributes_provided:
        logger.info('sso_after_process_request: add_attributes_to_response connected to function %s' % \
            attrs[0].__name__)
        if attrs[1] and attrs[1].has_key('attributes'):
            dic = attrs[1]
            logger.info('sso_after_process_request: attributes provided are %s' %str(dic['attributes']))
            for key in dic['attributes'].keys():
                attributes[key] = dic['attributes'][key]

    '''User consent management
       1- Check if it is required from the sp request, done in sso()
       2- Yes, check if a positive answer has already been given i.e. there is an existing federation
       3- No, Send signal to grab instructions to bypass consent
       4- No, ask for the user consent
       5- Yes, continue, No, return error to the service provider
    '''
    # TODO: manage the consentment on attributes
    # Use another model and another page

    if not consent_obtained and not transient:
        logger.info('sso_after_process_request: consent required')
        # If transient user, do not need consent for federation
        # Else, if there is a federation, the consent was already given
        try:
            LibertyFederation.objects.get(user=request.user, sp_id=login.remoteProviderId)
            logger.info('sso_after_process_request: consent already given (existing federation) for %s' %login.remoteProviderId)
            consent_obtained = True
        except:
            logger.info('sso_after_process_request: consent not already given (no existing federation) for %s' %login.remoteProviderId)

    # Signal to bypass user consent
    if not consent_obtained and not transient:
        logger.info('sso_after_process_request: signal avoid_consent sent')
        avoid_consent = idp_signals.avoid_consent.send(sender=None,
             request=request, user=request.user, audience=login.remoteProviderId)

        for c in avoid_consent:
            logger.info('sso_after_process_request: avoid_consent connected to function %s' % \
                c[0].__name__)
            if c[1] and c[1].has_key('avoid_consent') and c[1]['avoid_consent']:
                logger.info('sso_after_process_request: avoid_consent')
                consent_obtained = True

    if not consent_obtained and not transient:
        logger.info('sso_after_process_request: Ask the user consent now')
        return need_consent_for_federation(request, login, consent_obtained, save, nid_format)

    # XXX: Here treat with consent on attributes
    consent_attributes = True
    if not consent_attributes:
        logger.info('sso_after_process_request: consent for attribute propagation')
        request.session['attributes_to_send'] = attributes
        return need_consent_for_attributes(request, login, consent_obtained, save, nid_format)

    try:
        if not transient:
            logger.debug('sso_after_process_request: load identity dump')
            load_federation(request, login, user)
        load_session(request, login)
        logger.debug('sso_after_process_request: load session')
        login.validateRequestMsg(not user.is_anonymous(), consent_obtained)
        logger.debug('sso_after_process_request: validateRequestMsg')
    except lasso.LoginRequestDeniedError:
        logger.error('sso_after_process_request: access denied due to LoginRequestDeniedError')
        set_saml2_response_responder_status_code(login.response,
            lasso.SAML2_STATUS_CODE_REQUEST_DENIED)
        return finish_sso(request, login, user = user, save = save)
    except lasso.LoginFederationNotFoundError:
        logger.error('sso_after_process_request: access denied due to LoginFederationNotFoundError')
        set_saml2_response_responder_status_code(login.response,
                lasso.SAML2_STATUS_CODE_REQUEST_DENIED)
        return finish_sso(request, login, user = user, save = save)
    except:
        logger.error('sso_after_process_request: access denied due to unknown error')
        set_saml2_response_responder_status_code(login.response,
                lasso.SAML2_STATUS_CODE_REQUEST_DENIED)
        return finish_sso(request, login, user = user, save = save)

    build_assertion(request, login, nid_format = nid_format, attributes=attributes)
    return finish_sso(request, login, user = user, save = save)

def return_login_error(request, login, error):
    '''Set the first level status code to Responder, the second level to error
    and return the response message for the assertionConsumer'''
    logger.debug('return_login_error: error %s' %error)
    set_saml2_response_responder_status_code(login.response, error)
    return return_login_response(request, login)

def return_login_response(request, login):
    '''Return the AuthnResponse message to the assertion consumer'''
    if login.protocolProfile == lasso.LOGIN_PROTOCOL_PROFILE_BRWS_ART:
        login.buildArtifactMsg(lasso.HTTP_METHOD_ARTIFACT_GET)
        logger.info('return_login_response: sending Artifact to assertionConsumer %r' % login.msgUrl)
        save_artifact(request, login)
    elif login.protocolProfile == lasso.LOGIN_PROTOCOL_PROFILE_BRWS_POST:
        login.buildAuthnResponseMsg()
        logger.info('return_login_response: sending POST to assertionConsumer %r' % login.msgUrl)
        logger.debug('return_login_response: POST content %r' % login.msgBody)
    else:
        logger.error('return_login_response: NotImplementedError with login %s' %login.dump())
        raise NotImplementedError()
    return return_saml2_response(request, login, title = _('Authentication response'))

def finish_sso(request, login, user = None, save = False):
    logger.info('finish_sso: finishing sso...')
    if user is None:
        logger.debug('finish_sso: user is None')
        user=request.user
    response = return_login_response(request, login)
    if save:
        save_federation(request, login)
        logger.debug('finish_sso: federation saved')
        save_session(request, login)
        logger.debug('finish_sso: session saved')
    logger.info('finish_sso: sso treatment ended, send response')
    return response

def save_artifact(request, login):
    '''Remember an artifact message for later retrieving'''
    LibertyArtifact(artifact=login.artifact,
            content=login.artifactMessage,
            django_session_key=request.session.session_key,
            provider_id=login.remoteProviderId).save()
    logger.debug('save_artifact: artifact saved')

def reload_artifact(login):
    try:
        art = LibertyArtifact.objects.get(artifact=login.artifact)
        logger.debug('reload_artifact: artifact found')
        login.artifactMessage = art.content
        logger.debug('reload_artifact: artifact loaded')
        art.delete()
        logger.debug('reload_artifact: artifact deleted')
    except ObjectDoesNotExist:
        logger.debug('reload_artifact: no artifact found')
        pass

@csrf_exempt
def artifact(request):
    '''Resolve a SAMLv2 ArtifactResolve request
    '''
    logger.info('artifact: soap call received')
    soap_message = get_soap_message(request)
    logger.debug('artifact: soap message %r' %soap_message)
    server = create_server(request)
    login = lasso.Login(server)
    try:
        login.processRequestMsg(soap_message)
    except (lasso.ProfileUnknownProviderError, lasso.ParamError):
        if not load_provider(request, login.remoteProviderId,
                server=login.server):
            logger.error('artifact: provider loading failure')
        try:
            login.processRequestMsg(soap_message)
        except lasso.DsError, e:
            logger.error('artifact: signature error for %s: %s'
                    % (e, login.remoteProviderId))
        else:
            logger.info('artifact: reloading artifact')
            reload_artifact(login)
    except:
        logger.exception('artifact: resolve error')
    try:
        login.buildResponseMsg(None)
        logger.debug('artifact: resolve response %s' % login.msgBody)
    except:
        logger.exception('artifact: resolve error')
        return soap_fault(faultcode='soap:Server',
                faultstring='Internal Server Error')
    logger.info('artifact: treatment ended, return answer')
    return return_saml_soap_response(login)

def check_delegated_authentication_permission(request):
    logger.info('check_delegated_authentication_permission: superuser? %s' %str(request.user.is_superuser()))
    return request.user.is_superuser()

@login_required
def idp_sso(request, provider_id, user_id = None, nid_format = None):
    '''Initiate an SSO toward provider_id without a prior AuthnRequest
    '''
    if not provider_id:
        logger.info('idp_sso: to initiate a sso we need a provider_id')
        return error_page(request, _('A provider identifier was not provided'))
    logger.info('idp_sso: sso with %(provider_id)s' % { 'provider_id': provider_id })
    if user_id:
        logger.info('idp_sso: sso as %s' % user_id)
    server = create_server(request)
    login = lasso.Login(server)
    liberty_provider = load_provider(request, provider_id, server=login.server)
    if not liberty_provider:
        logger.info('idp_sso: sso for an unknown provider %s' % provider_id)
        return error_page(request, _('Provider %s is unknown') % provider_id)
    service_provider = liberty_provider.service_provider
    if user_id:
        user = User.get(id = user_id)
        if not check_delegated_authentication_permission(request):
            logger.warning('idp_sso: %r tried to log as %r on %r but was forbidden' % (
                                    request.user, user, provider_id))
            return HttpResponseForbidden('You must be superuser to log as another user')
    else:
        user = request.user
        logger.info('idp_sso: sso by %r' % user.username)
    load_federation(request, login, user)
    logger.debug('idp_sso: federation loaded')
    login.initIdpInitiatedAuthnRequest(provider_id)
    # Control assertion consumer binding
    binding = service_provider.prefered_assertion_consumer_binding
    logger.debug('idp_sso: binding is %r' %binding)
    if binding == 'meta':
        pass
    elif binding == 'art':
        login.request.protocolProfile = lasso.SAML2_METADATA_BINDING_ARTIFACT
    elif binding == 'post':
        login.request.protocolProfile = lasso.SAML2_METADATA_BINDING_POST
    else:
        logger.error('idp_sso: unsupported protocol binding %r' % binding)
        return error_page(request, _('Server error'))
    # Control nid format policy
    if nid_format:
        logger.debug('idp_sso: nameId format is %r' %nid_format)
        if not nid_format in service_provider.accepted_name_id_format:
            logger.error('idp_sso: name id format %r is not supported by %r' % (nid_format, provider_id))
            raise Http404('Provider %r does not support this name id format' % provider_id)
    if not nid_format:
        nid_format = service_provider.default_name_id_format
        logger.debug('idp_sso: nameId format is %r' %nid_format)
    login.processAuthnRequestMsg(None)

    return sso_after_process_request(request, login,
            consent_obtained = True, user = user, save = False, nid_format = nid_format)

def finish_slo(request):
    id = request.REQUEST.get('id')
    if not id:
        return HttpResponseBadRequest('finish_slo needs an id argument')
    logout_dump, session_key = get_and_delete_key_values(id)
    server = create_server(request)
    logout = lasso.Logout.newFromDump(server, logout_dump)
    load_provider(request, logout.remoteProviderId, server=logout.server)
    # Clean all session
    all_sessions = LibertySession.objects.filter(django_session_key=session_key)
    if all_sessions.exists():
        all_sessions.delete()
        return return_logout_error(logout, lasso.SAML2_STATUS_CODE_PARTIAL_LOGOUT)
    try:
        logout.buildResponseMsg()
    except:
        logger.exception('SAMLv2 slo failure to build reponse msg')
        raise NotImplementedError()
    return return_saml2_response(request, logout)

def return_logout_error(logout, error):
    logout.buildResponseMsg()
    set_saml2_response_responder_status_code(logout.response, error)
    # Hack because response is not initialized before
    # buildResponseMsg
    logout.buildResponseMsg()
    return return_saml2_response(request, logout)

def process_logout_request(request, message, binding):
    '''Do the first part of processing a logout request'''
    server = create_server(request)
    logout = lasso.Logout(server)
    if not message:
        return logout, HttpResponseBadRequest('No message was present')
    logger.debug('SAMLv2 slo with binding %s message %s' % (binding, message))
    try:
        try:
            logout.processRequestMsg(message)
        except (lasso.ServerProviderNotFoundError, lasso.ProfileUnknownProviderError), e:
            p = load_provider(request, logout.remoteProviderId,
                    server=logout.server)
            if not p:
                logger.error('SAMLv2 slo unknown provider %s' % logout.remoteProviderId)
                return logout, return_logout_error(logout,
                        AUTHENTIC_STATUS_CODE_UNKNOWN_PROVIDER)
            logout.processRequestMsg(message)
    except lasso.DsError, e:
        logger.error('SAMLv2 slo signature error on request %s' % message)
        return logout, return_logout_error(logout,
                lasso.LIB_STATUS_CODE_INVALID_SIGNATURE)
    except Exception, e:
        logger.error('SAMLv2 slo unknown error when processing a request %s' % message)
        return logout, HttpResponseBadRequest('Invalid logout request')
    if binding != 'SOAP' and not check_destination(request, logout.request):
        logger.error('SAMLv2 slo wrong or absent destination')
        return logout, return_logout_error(AUTHENTIC_STATUS_CODE_MISSING_DESTINATION)
    return logout, None

def log_logout_request(logout):
    name_id = nameid2kwargs(logout.request.nameId)
    session_indexes = logout.request.sessionIndexes
    logger.info('SAMLv2 slo nameid: %s session_indexes: %s' % (name_id,
        session_indexes))

def validate_logout_request(request, logout, idp=True):
    if not isinstance(logout.request.nameId, lasso.Saml2NameID):
        logger.error('SAMLv2 slo request lacks a NameID')
        return return_logout_error(logout,
                AUTHENTIC_STATUS_CODE_MISSING_NAMEID)
    # only idp have the right to send logout request without session indexes
    if not logout.request.sessionIndexes and idp:
        logger.error('SAMLv2 slo request lacks SessionIndex')
        return return_logout_error(logout,
                AUTHENTIC_STATUS_CODE_MISSING_SESSION_INDEX)
    log_logout_request(logout)
    return None

def logout_synchronous_other_backends(request, logout, django_sessions_keys):
    backends = idp.get_backends()
    ok = True
    for backend in backends:
        ok = ok and backends.can_synchronous_logout(django_sessions_keys)
    if not ok:
        return return_logout_error(logout,
                lasso.SAML2_STATUS_CODE_UNSUPPORTED_BINDING)
    return None

def get_only_last_session(name_id, session_indexes, but_provider):
    '''Try to have a decent behaviour when receiving a logout request with
       multiple session indexes.

       Enumerate all emitted assertions for the given session, and for each provider only keep the more recent one.
    '''
    logger.debug('get_only_last_session %s %s' % (name_id.dump(), session_indexes))
    lib_session1 = LibertySession.get_for_nameid_and_session_indexes(
            name_id, session_indexes)
    django_session_keys = [ s.django_session_key for s in lib_session1 ]
    lib_session = LibertySession.objects.filter(
            django_session_key__in=django_session_keys)
    providers = set([s.provider_id for s in lib_session])
    result = []
    for provider in providers:
        if provider != but_provider:
            x = lib_session.filter(provider_id=provider)
            latest = x.latest('creation')
            result.append(latest)
    return lib_session1, result, django_session_keys

def build_session_dump(elements):
    '''Build a session dump from a list of pairs
       (provider_id,assertion_content)'''
    session = [u'<Session xmlns="http://www.entrouvert.org/namespaces/lasso/0.0" Version="2">']
    for x in elements:
        session.append(u'<Assertion RemoteProviderID="%s">%s</Assertion>' % x)
    session.append(u'</Session>')
    return ''.join(session)

def set_session_dump_from_liberty_sessions(profile, lib_sessions):
    '''Extract all assertion from a list of lib_sessions, and create a session
    dump from them'''
    l = [(lib_session.provider_id, lib_session.assertion.assertion) \
            for lib_session in lib_sessions]
    profile.setSessionFromDump(build_session_dump(l).encode('utf8'))

@csrf_exempt
def slo_soap(request):
    """Endpoint for receiveing saml2:AuthnRequest by SOAP"""
    message = get_soap_message(request)
    logout, response = process_logout_request(request, message, 'SOAP')
    if response:
        return response
    response = validate_logout_request(request, logout, idp=True)
    if response:
        return response
    found, lib_sessions, django_session_keys = \
            get_only_last_session(logout.request.nameId,
                    logout.request.sessionIndexes, logout.remoteProviderId)
    if not found:
        return return_logout_error(logout, AUTHENTIC_STATUS_CODE_UNKNOWN_SESSION)
    for lib_session in lib_sessions:
        p = load_provider(request, lib_session.provider_id,
                server=logout.provider)
        if not p:
            logger.error('SAMLv2 slo cannot logout provider %s, it is no more \
known.' % lib_session.provider_id)
            continue
    set_session_dump_from_liberty_sessions(logout, found[0:1] + lib_sessions)
    try:
        logout.validateRequest()
    except lasso.LogoutUnsupportedProfileError, e:
        logger.error('SAMLv2 slo cannot do SOAP logout, one provider does \
not support it %s' % [ s.provider_id for s in lib_sessions])
        logout.buildResponseMsg()
        return return_saml2_response(request, logout)
    except Exception, e:
        logger.exception('SAMLv2 slo, unknown error')
        logout.buildResponseMsg()
        return return_saml2_response(request, logout)
    kill_django_sessions(django_session_keys)
    for lib_session in lib_sessions:
        try:
            logger.info('SAMLv2 slo, relaying logout to provider %s' % lib_session.provider_id)
            logout.initRequest(lib_session.provider_id)
            logout.buildRequestMsg()
            soap_response = send_soap_request(request, logout)
            logout.processResponseMsg(soap_response)
        except lasso.ProfileNotSuccessError:
            logger.error('SAMLv2 slo, SOAP realying failed for %s' % lib_session.provider_id)
        except:
            logger.exception('SAMLv2 slo, relaying failed %s' %
                    lib_session.provider_id)
    try:
        logout.buildResponseMsg()
    except:
        logger.exception('SAMLv2 slo failure to build reponse msg')
        raise NotImplementedError()
    return return_saml2_response(request, logout)

@csrf_exempt
def slo(request):
    """Endpoint for receiving saml2:AuthnRequests by POST, Redirect.
       For SOAP a session must be established previously through the login page. No authentication through the SOAP request is supported.
    """
    message = get_saml2_request_message_async_binding(request)
    logout, response = process_logout_request(request, message, request.method)
    if response:
        return response
    logger.debug('SAMLv2 asynchronous slo message %s' % message)
    try:
        try:
            logout.processRequestMsg(message)
        except (lasso.ServerProviderNotFoundError, lasso.ProfileUnknownProviderError), e:
            load_provider(request, logout.remoteProviderId,
                    server=logout.server)
            logout.processRequestMsg(message)
    except lasso.DsError, e:
        logger.exception('SAMLv2 signature error %s' % e)
        logout.buildResponseMsg()
        return return_saml2_response(request, logout, title=_('Logout response'))
    except Exception, e:
        logger.exception('SAMLv2 slo %s' % message)
        return error_page(_('Invalid logout request'))
    session_indexes = logout.request.sessionIndexes
    if len(session_indexes) == 0:
        logger.error('SAMLv2 slo received a request from %s without any SessionIndex, it is forbidden' % logout.remoteProviderId)
        logout.buildResponseMsg()
        return return_saml2_response(request, logout, title=_('Logout response'))
    logger.info('SAMLv2 asynchronous slo from %s' % logout.remoteProviderId)
    # Filter sessions
    all_sessions = LibertySession.get_for_nameid_and_session_indexes(
            logout.request.nameId, logout.request.sessionIndexes)
    # Does the request is valid ?
    remote_provider_sessions = \
            all_sessions.filter(provider_id=logout.remoteProviderId)
    if not remote_provider_sessions.exists():
        logger.error('SAMLv2 slo refused, since no session exists with the \
            requesting provider')
        return return_logout_error(logout, AUTHENTIC_STATUS_CODE_UNKNOWN_SESSION)
    # Load session dump for the requesting provider
    last_session = remote_provider_sessions.latest('creation')
    set_session_dump_from_liberty_sessions(logout, [last_session])
    try:
        logout.validateRequest()
    except:
        logger.exception('SAMLv2 slo error')
        return return_logout_error(logout,
                AUTHENTIC_STATUS_CODE_INTERNAL_SERVER_ERROR)
    # Now clean sessions for this provider
    LibertySession.objects.filter(provider_id=logout.remoteProviderId,
            django_session_key=request.session.session_key).delete()
    # Save some values for cleaning up
    save_key_values(logout.request.id, logout.dump(),
            request.session.session_key)
    return idp_views.redirect_to_logout(request, next_page='%s?id=%s' %
            (reverse(finish_slo), urllib.quote(logout.request.id)))

def ko_icon(request):
    return HttpResponseRedirect('%s/images/ko.png' % settings.MEDIA_URL)

def ok_icon(request):
    return HttpResponseRedirect('%s/images/ok.png' % settings.MEDIA_URL)

def redirect_next(request, next):
    if next:
        return HttpResponseRedirect(next)
    else:
        return None

@login_required
def idp_slo(request, provider_id):
    '''Send a single logout request to a SP, if given a next parameter, return
    to this URL, otherwise redirect to an icon symbolizing failure or success
    of the request

    provider_id - entity id of the service provider to log out
    all - if present, logout all sessions by omitting the SessionIndex element
    '''
    all = request.REQUEST.get('all')
    next = request.REQUEST.get('next')
    if not provider_id:
        return error_page('Missing argument provider_id')
    server = create_server(request)
    logout = lasso.Logout(server)
    logger.info('SAMLv2 idp_slo for %s' % provider_id)
    if not load_provider(request, provider_id, server=logout.server):
        logger.error('SAMLv2 idp_slo failed to load provider')
    lib_session = LibertySession.objects.filter(
            django_session_key=request.session.session_key,
            provider_id=provider_id).latest('creation')
    if lib_session:
        set_session_dump_from_liberty_sessions(logout, [lib_session])
    try:
        logout.initRequest(provider_id)
    except lasso.ProfileMissingAssertionError:
        logger.error('SAMLv2 idp_slo failed because no sessions exists for %r' % provider_id)
        return redirect_next(request, next) or ko_icon(request)
    if all is not None:
        logout.request.sessionIndexes = []
    logout.msgRelayState = logout.request.id
    try:
        logout.buildRequestMsg()
    except:
        logger.exception('SAMLv2 idp_slo misc error')
        return redirect_next(request, next) or ko_icon(request)
    if logout.msgBody: # SOAP case
        logger.info('SAMLv2 idp_slo by SOAP')
        try:
            soap_response = send_soap_request(request, logout)
        except:
            logger.exception('SAMLv2 idp_slo SOAP failure')
            return redirect_next(request, next) or ko_icon(request)
        return process_logout_response(request, logout, soap_response, next)
    else:
        logger.info('SAMLv2 idp_slo by redirect')
        save_key_values(logout.request.id, logout.dump(), provider_id, next)
        return HttpResponseRedirect(logout.msgUrl)

def process_logout_response(request, logout, soap_response, next):
    try:
        logout.processRequestMsg(soap_response)
    except:
        logger.exception('SAMLv2 slo error')
        return redirect_next(request, next) or ko_icon(request)
    else:
        LibertySession.objects.filter(
                    django_session_key=request.session.session_key,
                    provider_id=logout.remoteProviderId).delete()
        return redirect_next(request, next) or ok_icon(request)

def slo_return(request):
    relay_state = request.REQUEST.get('RelayState')
    if not relay_state:
        logger.error('SAMLv2 idp_slo no relay state in response')
        return error_page('Missing relay state')
    try:
        logout_dump, provider_id, next = get_and_delete_key_values(relay_state)
    except:
        logger.exception('SAMLv2 idp_slo bad relay state in response')
        return error_page('Bad relay state')
    server = create_server(request)
    logout = lasso.Logout.newFromDump(server, logout_dump)
    return process_logout_response(request, logout, get_saml2_query_request(request))

# Helpers

# SAMLv2 IdP settings variables
__local_options = getattr(settings, 'IDP_SAML2_METADATA_OPTIONS', {})
__user_backend_from_session = getattr(settings,
        'IDP_SAML2_AUTHN_CONTEXT_FROM_SESSION', True)
__delta = getattr(settings, 'IDP_SECONDS_TOLERANCE', 60)

# Mapping to generate the metadata file, must be kept in sync with the url
# dispatcher

def get_provider_id_and_options(request, provider_id):
    if not provider_id:
        provider_id=reverse(metadata)
    options = metadata_options
    options.update(__local_options)
    return provider_id, options

def get_metadata(request, provider_id=None):
    '''Generate the metadata XML file

       Metadata options can be overriden by setting IDP_METADATA_OPTIONS in
       settings.py.
    '''
    provider_id, options = get_provider_id_and_options(request, provider_id)
    return get_saml2_metadata(request, request.path, idp_map=metadata_map,
            options=metadata_options)


__cached_server = None
def create_server(request, provider_id=None):
    '''Build a lasso.Server object using current settings for the IdP

    The built lasso.Server is cached for later use it should work until
    multithreading is used, then thread local storage should be used.
    '''
    global __cached_server
    if __cached_server:
        # clear loaded providers
        __cached_server.providers = {}
        return __cached_server
    provider_id, options = get_provider_id_and_options(request, provider_id)
    __cached_server = create_saml2_server(request, provider_id,
            idp_map=metadata_map, options=options)
    return __cached_server

def log_info_authn_request_details(login):
    '''Push to logs details abour the received AuthnRequest'''
    request = login.request
    details = { 'issuer': login.request.issuer and login.request.issuer.content,
            'forceAuthn': login.request.forceAuthn,
            'isPassive': login.request.isPassive,
            'protocolBinding': login.request.protocolBinding }
    nameIdPolicy = request.nameIdPolicy
    if nameIdPolicy:
        details['nameIdPolicy'] = {
                'allowCreate': nameIdPolicy.allowCreate,
                'format': nameIdPolicy.format,
                'spNameQualifier': nameIdPolicy.spNameQualifier }

    logger.info('SAMLv2 authn request details: %r' % details)

def check_destination(request, req_or_res):
    '''Check that a SAML message Destination has the proper value'''
    destination = request.build_absolute_uri(request.path)
    result = req_or_res.destination == destination
    if not result:
        logger.error('SAMLv2 check_destination failed, expected: %s got: %s ' % (destination, req_or_res.destination))
    return result

urlpatterns = patterns('',
    (r'^metadata$', metadata),
    (r'^sso$', sso),
    (r'^continue$', continue_sso),
    (r'^slo$', slo),
    (r'^slo/soap$', slo_soap),
    (r'^idp_slo/(.*)$', idp_slo),
    (r'^slo_return$', slo_return),
    (r'^finish_slo$', finish_slo),
    (r'^artifact$', artifact),
    (r'^idp_sso/(.*)$', idp_sso),
    (r'^idp_sso/([^/]*)/([^/]*)$', idp_sso),
    (r'^idp_sso/([^/]*)/([^/]*)/([^/]*)$', idp_sso),
)
