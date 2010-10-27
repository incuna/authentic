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


import authentic2.idp as idp
import authentic2.idp.views as idp_views
from authentic2.saml.models import *
from authentic2.saml.common import *
import authentic2.saml.saml2utils as saml2utils
from authentic2.idp.models import AuthenticationEvent
from common import redirect_to_login, NONCE, kill_django_sessions

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

#####
# SSO
#####
def register_new_saml2_session(request, login, federation=None):
    '''Persist the newly created session for emitted assertion'''
    lib_assertion = LibertyAssertion(saml2_assertion=login.assertion)
    lib_assertion.save()
    lib_session = LibertySession(provider_id=login.remoteProviderId,
            saml2_assertion=login.assertion, federation=federation,
            django_session_key=request.session.session_key,
            assertion=lib_assertion)
    lib_session.save()

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
    else:
        # It should not happen as the nid_format has been checked
        # before
        assert False

def build_assertion(request, login, nid_format = 'transient'):
    '''After a successfully validated authentication request, build an
       authentication assertion'''
    now = datetime.datetime.utcnow()
    # 1 minute ago
    notBefore = now-datetime.timedelta(0,__delta)
    # 1 minute in the future
    notOnOrAfter = now+datetime.timedelta(0,__delta)
    ssl = request.environ.has_key('HTTPS')
    if __user_backend_from_session:
        backend = request.session[BACKEND_SESSION_KEY]
        if backend in ('django.contrib.auth.backends.ModelBackend',
                'authentic2.idp.auth_backends.LogginBackend'):
            if ssl:
                authn_context = lasso.SAML2_AUTHN_CONTEXT_PASSWORD_PROTECTED_TRANSPORT
            else:
                authn_context = lasso.SAML2_AUTHN_CONTEXT_PASSWORD
        elif backend == 'authentic2.sslauth.backends.SSLAuthBackend':
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
            elif auth_event.how == 'ssl':
                authn_context = lasso.LASSO_SAML2_AUTHN_CONTEXT_X509
            else:
                raise NotImplementedError('Unknown authentication method %r' % auth_event.how)
        except ObjectDoesNotExist:
            # TODO: previous session over secure transport (ssl) ?
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
        kwargs = nameid2kwargs(login.assertion.subject.nameID)
        federation, new = LibertyFederation.objects.get_or_create(
                idp_id=login.server.providerId,
                sp_id=login.remoteProviderId,
                user=request.user, **kwargs)
        if new:
            federation.save()
    else:
        federation = None
    register_new_saml2_session(request, login, federation=federation)

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
            return return_login_response(request, login)
        except (lasso.ServerProviderNotFoundError,
                lasso.ProfileUnknownProviderError):
            log_info_authn_request_details(login)
            provider_id = login.remoteProviderId
            provider_loaded = load_provider(request, login, provider_id)
            if not provider_loaded:
                consent_obtained = False
                message = _('SAMLv2: provider %r unknown') % provider_id
                logging.warning(message)
                return error_page(request, message)
            else:
                consent_obtained = \
                        not provider_loaded.service_provider.ask_user_consent
    if not check_destination(request, login.request):
        logging.error('SAMLv2 slo wrong or absent destination')
        return return_login_error(request, login,
                AUTHENTIC_STATUS_CODE_MISSING_DESTINATION)
    # Check NameIDPolicy or force the NameIDPolicy
    name_id_policy = login.request.nameIdPolicy
    if name_id_policy.format and \
            name_id_policy.format != \
                lasso.SAML2_NAME_IDENTIFIER_FORMAT_UNSPECIFIED:
        nid_format = saml2_urn_to_nidformat(name_id_policy.format)
        default_nid_format = provider_loaded.service_provider.default_name_id_format
        accepted_nid_format = \
                provider_loaded.service_provider.accepted_name_id_format
        if (not nid_format or nid_format not in accepted_nid_format) and \
           default_nid_format != nid_format:
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
        load_federation(request, login, user)
        load_session(request, login)
        login.validateRequestMsg(not user.is_anonymous(), consent_obtained)
    except lasso.LoginRequestDeniedError:
        do_federation = False
    except:
        logging.exception('SAMLv2 sso error')
        do_federation = False
    else:
        do_federation = True
    # 5. Lookup the federations
    if do_federation:
        # 3. Build and assertion, fill attributes
        build_assertion(request, login, nid_format = nid_format)
    return finish_sso(request, login, user = user, save = save)

def return_login_error(request, login, error):
    '''Set the first level status code to Responder, the second level to error
    and return the response message for the assertionConsumer'''
    set_saml2_response_responder_status_code(login.response, error)
    return return_login_response(request, login)

def return_login_response(request, login):
    '''Return the AuthnResponse message to the assertion consumer'''
    if login.protocolProfile == lasso.LOGIN_PROTOCOL_PROFILE_BRWS_ART:
        login.buildArtifactMsg(lasso.HTTP_METHOD_ARTIFACT_GET)
        logging.info('SAMLv2 sending Artifact to assertionConsumer %r' % login.msgUrl)
        save_artifact(request, login)
    elif login.protocolProfile == lasso.LOGIN_PROTOCOL_PROFILE_BRWS_POST:
        login.buildAuthnResponseMsg()
        logging.info('SAMLv2 sending POST to assertionConsumer %r' % login.msgUrl)
        logging.debug('SAMLv2 POST content %r' % login.msgBody)
    else:
        raise NotImplementedError()
    return return_saml2_response(login, title = _('Authentication response'))

def finish_sso(request, login, user = None, save = False):
    if user is None:
        user=request.user
    response = return_login_response(request, login)
    if save:
        save_federation(request, login)
        save_session(request, login)
    return response

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
    logging.debug('SAMLv2 artifact resolve %r' % soap_message)
    try:
        login.processRequestMsg(soap_message)
    except (lasso.ProfileUnknownProviderError, lasso.ParamError):
        if not load_provider(request, login, login.remoteProviderId):
            raise
        try:
            login.processRequestMsg(soap_message)
        except lasso.DsError, e:
            logging.error('SAMLv2 artifact resolve, signature error for %s: %s'
                    % (e, login.remoteProviderId))
        else:
            logging.info('Reloading artifact')
            reload_artifact(login)
    except:
        logging.exception('SAMLv2 artifact resolve error')
    try:
        login.buildResponseMsg(None)
        logging.debug('SAMLv2 artifact resolve response %s' % login.msgBody)
    except:
        logging.exception('SAMLv2 artifact resolve error')
        return soap_fault(faultcode='soap:Server',
                faultstring='Internal Server Error')
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
        raise error_page(request, _('Provider %s is unknown') % provider_id)
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
            logging.error('SAMLv2 idp_sso name id format %r is not supported by %r' % (nid_format, provider_id))
            raise Http404('Provider %r does not support this name id format' % provider_id)
    if not nid_format:
        nid_format = service_provider.default_name_id_format
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
    load_provider(request, logout, logout.remoteProviderId)
    # Clean all session
    all_sessions = LibertySession.objects.filter(django_session_key=session_key)
    if all_sessions.exists():
        all_sessions.delete()
        return return_logout_error(logout, lasso.SAML2_STATUS_CODE_PARTIAL_LOGOUT)
    try:
        logout.buildResponseMsg()
    except:
        logging.exception('SAMLv2 slo failure to build reponse msg')
        raise NotImplementedError()
    return return_saml2_response(logout)

def return_logout_error(logout, error):
    logout.buildResponseMsg()
    set_saml2_response_responder_status_code(logout.response, error)
    # Hack because response is not initialized before
    # buildResponseMsg
    logout.buildResponseMsg()
    return return_saml2_response(logout)

def process_logout_request(request, message, binding):
    '''Do the first part of processing a logout request'''
    server = create_server(request)
    logout = lasso.Logout(server)
    if not message:
        return logout, HttpResponseBadRequest('No message was present')
    logging.debug('SAMLv2 slo with binding %s message %s' % (binding, message))
    try:
        try:
            logout.processRequestMsg(message)
        except (lasso.ServerProviderNotFoundError, lasso.ProfileUnknownProviderError), e:
            p = load_provider(request, logout, logout.remoteProviderId)
            if not p:
                logging.error('SAMLv2 slo unknown provider %s' % logout.remoteProviderId)
                return logout, return_logout_error(logout,
                        AUTHENTIC_STATUS_CODE_UNKNOWN_PROVIDER)
            logout.processRequestMsg(message)
    except lasso.DsError, e:
        logging.error('SAMLv2 slo signature error on request %s' % message)
        return logout, return_logout_error(logout,
                lasso.LIB_STATUS_CODE_INVALID_SIGNATURE)
    except Exception, e:
        logging.error('SAMLv2 slo unknown error when processing a request %s' % message)
        return logout, HttpResponseBadRequest('Invalid logout request')
    if binding != 'SOAP' and not check_destination(request, logout.request):
        logging.error('SAMLv2 slo wrong or absent destination')
        return logout, return_logout_error(AUTHENTIC_STATUS_CODE_MISSING_DESTINATION)
    return logout, None

def log_logout_request(logout):
    name_id = nameid2kwargs(logout.request.nameId)
    session_indexes = logout.request.sessionIndexes
    logging.info('SAMLv2 slo nameid: %s session_indexes: %s' % (name_id,
        session_indexes))

def validate_logout_request(request, logout, idp=True):
    if not isinstance(logout.request.nameId, lasso.Saml2NameID):
        logging.error('SAMLv2 slo request lacks a NameID')
        return return_logout_error(logout,
                AUTHENTIC_STATUS_CODE_MISSING_NAMEID)
    # only idp have the right to send logout request without session indexes
    if not logout.request.sessionIndexes and idp:
        logging.error('SAMLv2 slo request lacks SessionIndex')
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
    logging.debug('get_only_last_session %s %s' % (name_id.dump(), session_indexes))
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
    session = ['<Session xmlns="http://www.entrouvert.org/namespaces/lasso/0.0" Version="2">']
    for x in elements:
        session.append('<Assertion RemoteProviderID="%s">%s</Assertion>' % x)
    session.append('</Session>')
    return ''.join(session)

def set_session_dump_from_liberty_sessions(profile, lib_sessions):
    '''Extract all assertion from a list of lib_sessions, and create a session
    dump from them'''
    l = [(lib_session.provider_id, lib_session.assertion.assertion) \
            for lib_session in lib_sessions]
    profile.setSessionFromDump(build_session_dump(l))

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
        p = load_provider(request, logout, lib_session.provider_id)
        if not p:
            logging.error('SAMLv2 slo cannot logout provider %s, it is no more \
known.' % lib_session.provider_id)
            continue
    set_session_dump_from_liberty_sessions(logout, found[0:1] + lib_sessions)
    try:
        logout.validateRequest()
    except lasso.LogoutUnsupportedProfileError, e:
        logging.error('SAMLv2 slo cannot do SOAP logout, one provider does \
not support it %s' % [ s.provider_id for s in lib_sessions])
        logout.buildResponseMsg()
        return return_saml2_response(logout)
    except Exception, e:
        logging.exception('SAMLv2 slo, unknown error')
        logout.buildResponseMsg()
        return return_saml2_response(logout)
    kill_django_sessions(django_session_keys)
    for lib_session in lib_sessions:
        try:
            logging.info('SAMLv2 slo, relaying logout to provider %s' % lib_session.provider_id)
            logout.initRequest(lib_session.provider_id)
            logout.buildRequestMsg()
            soap_response = send_soap_request(request, logout)
            logout.processResponseMsg(soap_response)
        except lasso.ProfileNotSuccessError:
            logging.error('SAMLv2 slo, SOAP realying failed for %s' % lib_session.provider_id)
        except:
            logging.exception('SAMLv2 slo, relaying failed %s' %
                    lib_session.provider_id)
    try:
        logout.buildResponseMsg()
    except:
        logging.exception('SAMLv2 slo failure to build reponse msg')
        raise NotImplementedError()
    return return_saml2_response(logout)

@csrf_exempt
@login_required
def slo(request):
    """Endpoint for receiving saml2:AuthnRequests by POST, Redirect.
       For SOAP a session must be established previously through the login page. No authentication through the SOAP request is supported.
    """
    message = get_saml2_request_message_async_binding(request)
    logout, response = process_logout_request(request, message, request.method)
    if response:
        return response
    logging.debug('SAMLv2 asynchronous slo message %s' % message)
    try:
        try:
            logout.processRequestMsg(message)
        except (lasso.ServerProviderNotFoundError, lasso.ProfileUnknownProviderError), e:
            load_provider(request, logout, logout.remoteProviderId)
            logout.processRequestMsg(message)
    except lasso.DsError, e:
        logging.exception('SAMLv2 signature error %s' % e)
        logout.buildResponseMsg()
        return return_saml2_response(logout, title=_('Logout response'))
    except Exception, e:
        logging.exception('SAMLv2 slo %s' % message)
        return error_page(_('Invalid logout request'))
    session_indexes = logout.request.sessionIndexes
    if len(session_indexes) == 0:
        logging.error('SAMLv2 slo received a request from %s without any SessionIndex, it is forbidden' % logout.remoteProviderId)
        logout.buildResponseMsg()
        return return_saml2_response(logout, title=_('Logout response'))
    logging.info('SAMLv2 asynchronous slo from %s' % logout.remoteProviderId)
    # Filter sessions
    all_sessions = LibertySession.get_for_nameid_and_session_indexes(
            logout.request.nameId, logout.request.sessionIndexes)
    # Does the request is valid ?
    remote_provider_sessions = \
            all_sessions.filter(provider_id=logout.remoteProviderId)
    if not remote_provider_sessions.exists():
        logging.error('SAMLv2 slo refused, since no session exists with the \
requesting provider')
        return return_logout_error(logout, AUTHENTIC_STATUS_CODE_UNKNOWN_SESSION)
    # Load session dump for the requesting provider
    last_session = remote_provider_sessions.latest('creation')
    set_session_dump_from_liberty_sessions(logout, [last_session])
    try:
        logout.validateRequest()
    except:
        logging.exception('SAMLv2 slo error')
        return return_logout_error(logout,
                AUTHENTIC_STATUS_CODE_INTERNAL_SERVER_ERROR)
    # Now clean sessions for this provider
    remote_provider_sessions.delete()
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
    logging.info('SAMLv2 idp_slo for %s' % provider_id)
    if not load_provider(request, logout, provider_id):
        logging.error('SAMLv2 idp_slo failed to load provider')
    lib_session = LibertySession.objects.filter(
            django_session_key=request.session.session_key,
            provider_id=provider_id).latest('creation')
    if lib_session:
        set_session_dump_from_liberty_sessions(logout, [lib_session])
    try:
        logout.initRequest(provider_id)
    except lasso.ProfileMissingAssertionError:
        logging.error('SAMLv2 idp_slo failed because no sessions exists for %r' % provider_id)
        return redirect_next(request, next) or ko_icon(request)
    if all is not None:
        logout.request.sessionIndexes = []
    logout.msgRelayState = logout.request.id
    try:
        logout.buildRequestMsg()
    except:
        logging.exception('SAMLv2 idp_slo misc error')
        return redirect_next(request, next) or ko_icon(request)
    if logout.msgBody: # SOAP case
        logging.info('SAMLv2 idp_slo by SOAP')
        try:
            soap_response = send_soap_request(request, logout)
        except:
            logging.exception('SAMLv2 idp_slo SOAP failure')
            return redirect_next(request, next) or ko_icon(request)
        return process_logout_response(request, logout, soap_response, next)
    else:
        logging.info('SAMLv2 idp_slo by redirect')
        save_key_values(logout.request.id, logout.dump(), provider_id, next)
        return HttpRedirect(logout.msgUrl)

def process_logout_response(request, logout, soap_response, next):
    try:
        logout.processRequestMsg(soap_response)
    except:
        logging.exception('SAMLv2 slo error')
        return redirect_next(request, next) or ko_icon(request)
    else:
        LibertySession.objects.filter(
                    django_session_key=request.session.session_key,
                    provider_id=logout.remoteProviderId).delete()
        return redirect_next(request, next) or ok_icon(request)

def slo_return(request):
    relay_state = request.REQUEST.get('RelayState')
    if not relay_state:
        logging.error('SAMLv2 idp_slo no relay state in response')
        return error_page('Missing relay state')
    try:
        logout_dump, provider_id, next = get_and_delete_key_values(relay_state)
    except:
        logging.exception('SAMLv2 idp_slo bad relay state in response')
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
metadata_map = ((saml2utils.Saml2Metadata.SINGLE_SIGN_ON_SERVICE, asynchronous_bindings , '/sso'),
        (saml2utils.Saml2Metadata.SINGLE_LOGOUT_SERVICE, asynchronous_bindings, '/slo', '/slo_return'),
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

def check_destination(request, req_or_res):
    '''Check that a SAML message Destination has the proper value'''
    destination = request.build_absolute_uri(request.path)
    result = req_or_res.destination == destination
    if not result:
        logging.error('SAMLv2 check_destination failed, expected: %s got: %s ' % (destination, req_or_res.destination))
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

