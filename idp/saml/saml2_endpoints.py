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

from authentic.saml.models import *
from authentic.saml.common import *
import authentic.saml.saml2utils as saml2utils
from authentic.idp.models import AuthenticationEvent
from common import redirect_to_login, NONCE

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

def metadata(request):
    '''Endpoint to retrieve the metadata file'''
    return HttpResponse(get_metadata(request, request.path))

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
    # Use assertion ID as session index
    assertion.authnStatement[0].sessionIndex = assertion.id
    # NameID
    if nid_format in ('persistent', 'transient'):
        pass
    elif nid_format == 'email':
        assertion.subject.nameID.content = request.user.email

def build_assertion(request, login, nid_format = 'transient'):
    '''After a successfully validated authentication request, build an
       authentication assertion'''
    now = datetime.datetime.utcnow()
    # 1 minute ago
    notBefore = now-datetime.timedelta(0,60)
    # 1 minute in the future
    notOnOrAfter = now+datetime.timedelta(0,60)
    # TODO: find authn method from login event or from session
    use_user_backend = True
    if use_user_backend:
        backend = request.session[BACKEND_SESSION_KEY]
        if backend in ('django.contrib.auth.backends.ModelBackend',
                'authentic.idp.auth_backends.LogginBackend'):
            if request.environ.has_key('HTTPS'):
                authn_context = lasso.SAML2_AUTHN_CONTEXT_PASSWORD_PROTECTED_TRANSPORT
            else:
                authn_context = lasso.SAML2_AUTHN_CONTEXT_PASSWORD
        elif backend == 'authentic.sslauth.backends.SSLAuthBackend':
            authn_context = lasso.LASSO_SAML2_AUTHN_CONTEXT_X509
        else:
            raise Exception('unknown backend: ' + backend)
    else:
        try:
            auth_event = AuthenticationEvent.objects.get(nonce = login.request.id)
            if auth_event.how == 'password':
                authn_context = lasso.SAML2_AUTHN_CONTEXT_PASSWORD
            elif auth_event.how == 'password-on-https':
                authn_context = lasso.SAML2_AUTHN_CONTEXT_PASSWORD_PROTECTED_TRANSPORT
        except ObjectDoesNotExist:
            authn_context = lasso.SAML2_AUTHN_CONTEXT_PREVIOUS_SESSION
    login.buildAssertion(authn_context,
            now.isoformat()+'Z',
            'unused', # reauthenticateOnOrAfter is only for ID-FF 1.2
            notBefore.isoformat()+'Z',
            notOnOrAfter.isoformat()+'Z')
    assertion = login.assertion
    fill_assertion(request, login.request, assertion, login.remoteProviderId, nid_format)
    # Save federation and new session
    if login.assertion.subject.nameID.format == lasso.SAML2_NAME_IDENTIFIER_FORMAT_PERSISTENT:
        federation = LibertyFederation(saml2_assertion=login.assertion)
        federation.save()
    else:
        federation = None
    lib_assertion = LibertyAssertion(saml2_assertion=login.assertion)
    lib_assertion.save()
    LibertySession(saml2_assertion=login.assertion,assertion=lib_assertion,
            django_session_key=request.session.session_key,
            provider_id=login.remoteProviderId,
            federation=federation).save()


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

    logging.info('SAMLv2 authn request details: %r' % details)

@csrf_exempt
def sso(request):
    """Endpoint for receiving saml2:AuthnRequests by POST, Redirect or SOAP.
       For SOAP a session must be established previously through the login page. No authentication through the SOAP request is supported.
    """
    if request.method != 'GET':
        return HttpResponseForbidden('SAMLv2 sso endpoint only support HTTP-Redirect binding')
    message = get_saml2_request_message(request)
    server = create_server(request)
    login = lasso.Login(server)
    # 1. Process the request, separate POST and GET treatment
    if not message:
        return HttpResponseForbidden('SAMLv2 sso need a query string')
    logging.debug('SAMLv2: processing sso request %r' % message)
    while True:
        try:
            login.processAuthnRequestMsg(message)
            break
        except (lasso.ProfileInvalidMsgError,
            lasso.ProfileMissingIssuerError,), e:
            logging.error('SAMLv2: invalid message for WebSSO profile with '
                          'HTTP-Redirect binding: %r exception: %s' % (message, e))
            return HttpResponseBadRequest(_('SAMLv2: invalid message for '
                'WebSSO profile with HTTP-Redirect binding: %r') % message)
        except lasso.ProfileInvalidProtocolprofileError:
            log_info_authn_request_details(login)
            message = N_('SAMLv2: sso request cannot be answered because no valid protocol binding could be found')
            logging.error(message)
            return HttpResponseBadRequest(_(message))
        except lasso.DsError, e:
            log_info_authn_request_details(login)
            logging.error('SAMLv2: cryptographic error: %s' % e)
            return finish_sso(request, login)
        except (lasso.ServerProviderNotFoundError, lasso.ProfileUnknownProviderError):
            log_info_authn_request_details(login)
            provider_id = login.remoteProviderId
            provider_loaded = load_provider(request, login, provider_id)
            if not provider_loaded:
                consent_obtained = False
                message = _('SAMLv2: provider %r unknown') % provider_id
                logging.warning(message)
                return HttpResponseForbidden(message)
            else:
                consent_obtained = not provider_loaded.service_provider.ask_user_consent
    # Check NameIDPolicy or force the NameIDPolicy
    name_id_policy = login.request.nameIdPolicy
    if name_id_policy.format and \
            name_id_policy.format != \
                lasso.SAML2_NAME_IDENTIFIER_FORMAT_UNSPECIFIED:
        nid_format = saml2_urn_to_nidformat(name_id_policy.format)
        accepted_nid_format = \
                provider_loaded.service_provider.accepted_name_id_format
        if not nid_format or nid_format not in accepted_nid_format:
            set_saml2_response_responder_status_code(login.response,
                lasso.SAML2_STATUS_CODE_INVALID_NAME_ID_POLICY)
            return finish_sso(request, login)
    else:
        nid_format = provider_loaded.service_provider.default_name_id_format
        name_id_policy.format = nidformat_to_saml2_urn(nid_format)

    return sso_after_process_request(request, login,
        consent_obtained = consent_obtained, nid_format = nid_format)

def need_login(request, login, consent_obtained, save, nid_format):
    '''Redirect to the login page with a nonce parameter to verify later that
       the login form was submitted'''
    nonce = login.request.id
    save_key_values(nonce, login.dump(), consent_obtained, save, nid_format)
    return redirect_to_login(reverse(continue_sso)+'?%s=%s' % (NONCE, nonce),
            other_keys={'nonce': nonce})

def need_consent(request, login, consent_obtained, save, nid_format):
    nonce = login.request.id
    save_key_values(nonce, login.dump(), consent_obtained, save, nid_format)
    return HttpResponseRedirect('%s?%s=%s&next=%s' % (reverse(consent), NONCE,
        nonce, urllib.quote(request.get_full_path())) )

def continue_sso(request):
    nonce = request.REQUEST.get(NONCE, '')
    login_dump, consent_obtained, save, nid_format = \
            get_and_delete_key_values(nonce)
    server = create_server(request)
    login = lasso.Login.newFromDump(server, login_dump)
    if not load_provider(request, login, login.remoteProviderId):
        return HttpResponseBadRequest('Unknown provider')
    if not login:
        logging.debug('SAMLv2: continue sso nonce %r not found' % nonce)
        return HttpResponseBadRequest()
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

    if not passive and (user.is_anonymous() or (force_authn and not did_auth)):
        return need_login(request, login, consent_obtained, save, nid_format)
    # TODO: implement consent
    try:
        login.validateRequestMsg(not user.is_anonymous(), consent_obtained)
    except lasso.LoginRequestDeniedError:
        do_federation = False
    except:
        raise
        do_federation = False
    else:
        do_federation = True
    # 5. Lookup the federations
    if do_federation:
        load_federation(request, login, user)
        load_session(request, login)
        # 3. Build and assertion, fill attributes
        build_assertion(request, login, nid_format = nid_format)
    return finish_sso(request, login, user = user, save = save)

def finish_sso(request, login, user = None, save = False):
    if user is None:
        user=request.user
    if login.protocolProfile == lasso.LOGIN_PROTOCOL_PROFILE_BRWS_ART:
        logging.info('SAMLv2 finish_sso send Artifact to %r' % login.msgUrl)
        login.buildArtifactMsg(lasso.HTTP_METHOD_ARTIFACT_GET)
        save_artifact(request, login)
    elif login.protocolProfile == lasso.LOGIN_PROTOCOL_PROFILE_BRWS_POST:
        logging.info('SAMLv2 finish_sso send POST to %r' % login.msgUrl)
        logging.debug('SAMLv2 finish_sso POST content %r' % login.msgBody)
        login.buildAuthnResponseMsg()
    else:
        raise NotImplementedError()
    if save:
        save_federation(request, login)
        save_session(request, login)
        pass
    return return_saml2_response(login, title = _('Authentication response'))

def save_artifact(request, login):
    '''Remember an artifact message for later retrieving'''
    LibertyArtifact(artifact=login.artifact,
            content=login.artifactMessage,
            django_session_key=request.session.session_key,
            provider_id=login.remoteProviderId).save()

def reload_artifact(login):
    try:
        art = LibertyArtifact.objects.get(artifact=login.artifact)
        login.artifactMessage = art.content
        art.delete()
    except ObjectDoesNotExist:
        pass

@csrf_exempt
def artifact(request):
    '''Resolve a SAMLv2 ArtifactResolve request
    '''
    soap_message = get_soap_message(request)
    server = create_server(request)
    login = lasso.Login(server)
    try:
        login.processRequestMsg(soap_message)
    except (lasso.ProfileUnknownProviderError, lasso.ParamError):
        if not load_provider(request, login, login.remoteProviderId):
            raise
        login.processRequestMsg(soap_message)
    logging.debug('SAMLv2 artifact resolve %r' % soap_message)
    reload_artifact(login)
    try:
        login.buildResponseMsg(None)
    except:
        raise
    return return_saml_soap_response(login)

def check_delegated_authentication_permission(request):
    return request.user.is_superuser()

@login_required
def idp_sso(request, provider_id, user_id = None, nid_format = None):
    '''Initiate an SSO toward provider_id without a prior AuthnRequest
    '''
    assert provider_id, 'You must call idp_initiated_sso with a provider_id parameter'
    logging.info('SAMLv2 idp_sso to %(provider_id)s' % { 'provider_id': provider_id })
    if user_id:
        logging.info('SAMLv2 idp_sso as %s' % user_id)
    server = create_server(request)
    login = lasso.Login(server)
    liberty_provider = load_provider(request, login, provider_id)
    if not liberty_provider:
        logging.info('SAMLv2 idp_sso for an unknown provider %s' % provider_id)
        raise Http404('Provider %s is unknown' % provider_id)
    service_provider = liberty_provider.service_provider
    if user_id:
        user = User.get(id = user_id)
        if not check_delegated_authentication_permission(request):
            logging.warning('SAMLv2 idp_sso %r tried to log as %r on %r but was forbidden' % (
                                    request.user, user, provider_id))
            return HttpResponseForbidden('You must be superuser to log as another user')
    else:
        user = request.user
    load_federation(request, login, user)
    login.initIdpInitiatedAuthnRequest(provider_id)
    # Control assertion consumer binding
    binding = service_provider.prefered_assertion_consumer_binding
    if binding == 'meta':
        pass
    elif binding == 'art':
        login.request.protocolProfile = lasso.SAML2_METADATA_BINDING_ARTIFACT
    elif binding == 'post':
        login.request.protocolProfile = lasso.SAML2_METADATA_BINDING_POST
    else:
        logging.error('SAMLv2 idp_sso unsupported protocol binding %r' % binding)
        raise NotImplementedError()
    # Control nid format policy
    if nid_format:
        if not nid_format in service_provider.accepted_name_id_format:
            loggin.error('SAMLv2 idp_sso name id format %r is not supported by %r' % (nid_format, provider_id))
            raise Http404('Provider %r does not support this name id format' % provider_id)
    if not nid_format:
        nid_format = service_provider.default_name_id_format
    login.processAuthnRequestMsg(None)

    return sso_after_process_request(request, login,
            consent_obtained = True, user = user, save = False, nid_format = nid_format)

@csrf_exempt
def slo(request):
    """Endpoint for receiving saml2:AuthnRequests by POST, Redirect or SOAP.
       For SOAP a session must be established previously through the login page. No authentication through the SOAP request is supported.
    """
    pass

# Helpers

# SAMLv2 IdP settings variables
__local_options = getattr(settings, 'IDP_SAML2_METADATA_OPTIONS', {})
__user_backend_from_session = getattr(settings,
        'IDP_SAML2_AUTHN_CONTEXT_FROM_SESSION', True)
__delta = getattr(settings, 'IDP_SECONDS_TOLERANCE', 60)

# Mapping to generate the metadata file, must be kept in sync with the url
# dispatcher
metadata_map = ((saml2utils.Saml2Metadata.SINGLE_SIGN_ON_SERVICE, asynchronous_bindings , '/sso'),
        (saml2utils.Saml2Metadata.SINGLE_LOGOUT_SERVICE, asynchronous_bindings, '/slo', '/return_slo'),
        (saml2utils.Saml2Metadata.SINGLE_LOGOUT_SERVICE, soap_bindings, '/slo/soap'),
        (saml2utils.Saml2Metadata.ARTIFACT_RESOLUTION_SERVICE, lasso.SAML2_METADATA_BINDING_SOAP, '/artifact'))

metadata_options = { 'signing_key': settings.SAML_PRIVATE_KEY }

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

urlpatterns = patterns('',
    (r'^metadata$', metadata),
    (r'^sso', sso),
    (r'^slo', slo),
    (r'^artifact', artifact),
    (r'^continue', continue_sso),
    (r'^idp_sso/(.*)$', idp_sso),
    (r'^idp_sso/([^/]*)/([^/]*)$', idp_sso),
    (r'^idp_sso/([^/]*)/([^/]*)/([^/]*)$', idp_sso),

)

