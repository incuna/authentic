from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.contrib.auth import get_user
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext as _
import settings
import datetime, time
import logging
import lasso
from saml.common import *
from saml.models import *
from utils import *

#############################################
# SAML2 protocol
#############################################

def metadata(request):
    return HttpResponse(get_saml2_sp_metadata(request, reverse(metadata)), mimetype = 'text/xml')

###
 # sso
 # @request
 # @ entity_id: Provider ID to request
 #
 # Single SignOn request
 # Binding supported: Redirect
 ###
def sso(request, entity_id=None):
    s = get_service_provider_settings()
    if not s:
        return error_page(request, _('Service provider not configured'))
    # 1. Save the target page
    session_ext = register_next_target(request)
    if not session_ext:
        return error_page(request, _('Error handling session'))
    # 2. Init the server object
    server = build_service_provider(request)
    if not server:
        return error_page(request, _('Service provider not configured'))
    # 3. Define the provider or ask the user
    if not entity_id:
        providers_list = get_idp_list()
        if not providers_list:
            return error_page(request, 'Service provider not configured')
        if providers_list.count() == 1:
            p = providers_list[0]
        else:
            return render_to_response('idp_select.html', {'providers_list': providers_list},
                context_instance=RequestContext(request))
    else:
        try:
            p = LibertyProvider.objects.get(entity_id=entity_id)
        except LibertyProvider.DoesNotExist:
            return error_page(request, 'The provider does not exist')
    # 4. Build authn request
    login = lasso.Login(server)
    # Only redirect is necessary for the authnrequest
    login.initAuthnRequest(p.entity_id, lasso.HTTP_METHOD_REDIRECT)
    login.request.nameIDPolicy.format = lasso.SAML2_NAME_IDENTIFIER_FORMAT_PERSISTENT
    login.request.nameIDPolicy.allowCreate = True
    # TODO: set url for the assertion consumer
    if p.identity_provider.enable_binding_for_sso_response:
        login.request.protocolBinding = p.identity_provider.binding_for_sso_response
    login.request.forceAuthn = False
    login.request.isPassive = False
    login.request.consent = 'urn:oasis:names:tc:SAML:2.0:consent:current-implicit'
    login.buildAuthnRequestMsg()
    # 5. Save the request ID (association with the target page)
    session_ext.saml_request_id = login.request.iD
    session_ext.save()
    # 6. Redirect the user
    return HttpResponseRedirect(login.msgUrl)

def selectProvider(request, entity_id):
    return sso(request, entity_id=entity_id)

###
 # singleSignOnArtifact, singleSignOnPostOrRedirect
 # @request
 #
 # Single SignOn Response
 # Binding supported: Artifact, POST
 ###
def singleSignOnArtifact(request):
    server = build_service_provider(request)
    if not server:
        return error_page(request, _('Service provider not configured'))
    login = lasso.Login(server)
    message = get_saml2_request_message(request)
    try:
        if request.method == 'GET':
            login.initRequest(message, lasso.HTTP_METHOD_ARTIFACT_GET)
        else:
            login.initRequest(message, lasso.HTTP_METHOD_ARTIFACT_POST)
    except lasso.Error, error:
            return error_page(request, 'Invalid authentication response')
    login.buildRequestMsg()

    # TODO: Client certificate
    client_cert = None
    soap_answer = soap_call(login.msgUrl, login.msgBody, client_cert = client_cert)
    if not soap_answer:
        return template.error_page(_('Failure to communicate with identity provider'))

    try:
        login.processResponseMsg(soap_answer)
    except lasso.Error, error:
        if error[0] == lasso.LOGIN_ERROR_STATUS_NOT_SUCCESS:
            return error_page(request, _('Unknown authentication failure'))
        if error[0] == lasso.SERVER_ERROR_PROVIDER_NOT_FOUND:
            return error_page(request, _('Request from unknown provider ID'))
        if error[0] == lasso.DS_ERROR_SIGNATURE_NOT_FOUND:
            return error_page(request, _('Error checking signature'))
        if error[0] == lasso.DS_ERROR_SIGNATURE_VERIFICATION_FAILED:
            return error_page(request, _('Error checking signature'))
        if error[0] == lasso.DS_ERROR_INVALID_SIGNATURE:
            return error_page(request, _('Error checking signature'))
        return error_page(request, _('Unknown error processing authn response message'))
    # TODO: Relay State
    return sso_after_response(request, login)

@csrf_exempt
def singleSignOnPost(request):
    server = build_service_provider(request)
    if not server:
        error_page(request, _('Service provider not configured'))
    login = lasso.Login(server)
    # TODO: check messages = get_saml2_request_message(request)
    # Binding POST
    message = request.POST.__getitem__('SAMLResponse')
    # Binding REDIRECT
    # According to: saml-profiles-2.0-os
    # The HTTP Redirect binding MUST NOT be used, as the response will typically exceed the URL length permitted by most user agents.
    # if not message:
    #    message = request.META.get('QUERY_STRING', '')
    if not message:
        error_page(request, _('No message given.'))
    try:
        login.processAuthnResponseMsg(message)
    except lasso.Error, error:
        if error[0] == lasso.LOGIN_ERROR_STATUS_NOT_SUCCESS:
            return error_page(request, _('Unknown authentication failure'))
        if error[0] == lasso.SERVER_ERROR_PROVIDER_NOT_FOUND:
            return error_page(request, _('Request from unknown provider ID'))
        if error[0] == lasso.DS_ERROR_SIGNATURE_NOT_FOUND:
            return error_page(request, _('Error checking signature'))
        if error[0] == lasso.DS_ERROR_SIGNATURE_VERIFICATION_FAILED:
            return error_page(request, _('Error checking signature'))
        if error[0] == lasso.DS_ERROR_INVALID_SIGNATURE:
            return error_page(request, _('Error checking signature'))
        return error_page(request, _('Unknown error processing authn response message'))
    return sso_after_response(request, login)

###
 # sso_after_response
 # @request
 # @login
 # @relay_state
 #
 # Post-authnrequest process
 # TODO: Proxying
 ###
def sso_after_response(request, login, relay_state = None):
    # If there is no inResponseTo: IDP initiated
    # else, check that the response id is the same
    irt = None
    try:
        irt = login.response.assertion[0].subject.subjectConfirmation.subjectConfirmationData.inResponseTo
    except:
        return error_page(request, _('Assertion missing'))
    if irt and not check_response_id(login):
        return error_page(request, _('Response identifier does not match with request'))
    #TODO: Register assertion and check for replay
    assertion = login.response.assertion[0]
    # Check: Check that the url is the same as in the assertion
    try:
        if assertion.subject.subjectConfirmation.subjectConfirmationData.recipient != \
                request.build_absolute_uri().partition('?')[0]:
            return error_page(request, _('SubjectConfirmation Recipient Mismatch'))
    except:
            return error_page(request, _('Errot checking SubjectConfirmation Recipient'))
    # Check: SubjectConfirmation
    try:
        if assertion.subject.subjectConfirmation.method != \
                'urn:oasis:names:tc:SAML:2.0:cm:bearer':
            return error_page(request, _('Unknown SubjectConfirmation Method'))
    except:
        return error_page(request, _('Error checking SubjectConfirmation Method'))
    # Check: AudienceRestriction
    try:
        audience_ok = False
        for audience_restriction in assertion.conditions.audienceRestriction:
            if audience_restriction.audience != login.server.providerId:
                return error_page(request, _('Incorrect AudienceRestriction'))
            audience_ok = True
        if not audience_ok:
            return error_page(request, _('Incorrect AudienceRestriction'))
    except:
        return error_page(request, _('Error checking AudienceRestriction'))
    # Check: notBefore, notOnOrAfter
    try:
        now = datetime.datetime.utcnow()
        not_before = assertion.subject.subjectConfirmation.subjectConfirmationData.notBefore
        not_on_or_after = assertion.subject.subjectConfirmation.subjectConfirmationData.notOnOrAfter
        if not_before and now < datetime.datetime.fromtimestamp(time.mktime(time.strptime(not_before,"%Y-%m-%dT%H:%M:%SZ"))):
            return error_page(request, _('Assertion received too early'))
        if not_on_or_after and now > datetime.datetime.fromtimestamp(time.mktime(time.strptime(not_on_or_after,"%Y-%m-%dT%H:%M:%SZ"))):
            return error_page(request, _('Assertion expired'))
    except:
        return error_page(request, _('Error checking Assertion Time'))

    login.acceptSso()

    user = request.user
    if not request.user.is_anonymous():
        fed = lookup_federation_by_name_identifier(login)
        if fed:
            save_session(request, login)
            save_federation(request, login)
            maintain_liberty_session_on_service_provider(request, login)
            return redirect_to_target(request)
        else:
            fed = add_federation(user, login)
            if not fed:
                return error_page(request, _('Erreur adding new federation for this user'))
            save_session(request, login)
            save_federation(request, login)
            maintain_liberty_session_on_service_provider(request, login)
            return redirect_to_target(request)
    else:
        from backends import AuthSAML2Backend
        user = AuthSAML2Backend().authenticate(request,login)
        if user:
            key = request.session.session_key
            auth_login(request, user)
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            save_session(request, login)
            save_federation(request, login)
            maintain_liberty_session_on_service_provider(request, login)
            return redirect_to_target(request, key)
        else:
            s = get_service_provider_settings()
            if not s:
                return error_page(request, _('Service provider not configured'))
            #TODO: User unknown
            if s.unauth == 'AUTHSAML2_UNAUTH_ACCOUNT_LINKING_BY_AUTH':
                register_federation_in_progress(request,login.nameIdentifier.content)
                save_session(request, login)
                save_federation_temp(request, login)
                maintain_liberty_session_on_service_provider(request, login)
                return render_to_response('account_linking.html', context_instance=RequestContext(request))
                pass
            elif s.unauth == 'AUTHSAML2_UNAUTH_ACCOUNT_LINKING_BY_ATTRS':
                pass
            elif s.unauth == 'AUTHSAML2_UNAUTH_ACCOUNT_LINKING_BY_TOKEN':
                pass
            elif s.unauth == 'AUTHSAML2_UNAUTH_CREATE_USER_PSEUDONYMOUS':
                user = SAML2AuthBackend().create_user(nameId=login.nameIdentifier.content)
                key = request.session.session_key
                auth_login(request, user)
                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                save_session(request, login)
                maintain_liberty_session_on_service_provider(request, login)
                return redirect_to_target(request, key)
            elif s.unauth == 'AUTHSAML2_UNAUTH_CREATE_USER_PSEUDONYMOUS_ONE_TIME':
                pass
            elif s.unauth == 'AUTHSAML2_UNAUTH_CREATE_USER_WITH_ATTRS_IN_A8N':
                pass
            elif s.unauth == 'AUTHSAML2_UNAUTH_CREATE_USER_WITH_ATTRS_SELF_ASSERTED':
                pass
        #TODO: Relay state
        return error_page(request, _('Not yet implemented'))

###
 # register_federation_in_progres
 # @request
 # @nameId
 #
 # Register the post-authnrequest process during account linking
 ###
def register_federation_in_progress(request, nameId):
    session_ext = None
    try:
        session_ext = ExtendDjangoSession.objects.get(django_session_key=request.session.session_key)
        session_ext.federation_in_progress = nameId
        session_ext.save()
    except:
        pass
    if not session_ext:
        try:
            session_ext = ExtendDjangoSession()
            session_ext.django_session_key = request.session.session_key
            session_ext.federation_in_progress = nameId
            session_ext.save()
        except:
            pass 
    return session_ext

###
 # finish_federation
 # @request
 #
 # Called after an account linking.
 ###
@csrf_exempt
def finish_federation(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            server = build_service_provider(request)
            if not server:
                return error_page(request, _('Service provider not configured'))
            login = lasso.Login(server)
            s = load_session(request, login)
            load_federation_temp(request, login)
            if not login.session:
                return error_page(request, _('Error loading session.'))
            login.nameIdentifier = login.session.getAssertions()[0].subject.nameID
            fed = add_federation(form.get_user(), login)
            if not fed:
                return error_page(request, _('Error adding new federation for this user'))
            key = request.session.session_key
            auth_login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            s.delete()
            login.session.isDirty = True
            login.identity.isDirty = True
            save_session(request, login)
            save_federation(request, login)
            maintain_liberty_session_on_service_provider(request, login)
            return redirect_to_target(request, key)
        else:
            # TODO: Error: login failed: message and count 3 attemps
            return render_to_response('account_linking.html', context_instance=RequestContext(request))
    else:
        return error_page(request, _('Unable to perform federation'))

# TODO: We do not manage mutliple login.
# There is only one global logout possible.
# Then, remove the function "federate your identity" under a sso session.
# Multiple login should not be for a SSO purpose but to obtain "membership cred" or "attributes".
# Then, Idp sollicited for such creds should not maintain a session after the credential issuing.
# Multiple logout: Tell the user on which idps, the user is logged
# Propose local or global logout
# for global, break local session only when there is only idp logged remaining

###
 # logout
 # @request
 # @method
 # @entity_id
 #
 # Single Logout Request
 # Assumed that the principal is logged on a single IdP
 # The provider is given in parameter, also in the session.
 # Profile supported: Redirect, SOAP
 # For response, if the requester uses a (a)synchronous binding, the responder uses the same.
 # Else, the grabs the preferred method from the metadata.
 # TODO: IdP initiated
 ###
def logout(request):
    if not is_sp_configured():
        return error_page(request, _('Service provider not configured'))
    if request.user.is_anonymous():
        return error_page(request, _('Unable to logout a not logged user!'))
    server = build_service_provider(request)
    if not server:
        error_page(request, _('Service provider not configured'))
    logout = lasso.Logout(server)
    load_session(request, logout)
    # Lookup for the Identity provider from session
    q = LibertySessionDump.objects.filter(django_session_key = request.session.session_key)
    if not q:
        return error_page(request, _('No session for global logout.'))
    try:
        pid = lasso.Session().newFromDump(q[0].session_dump).get_assertions().keys()[0]
        p = LibertyProvider.objects.get(entity_id=pid)
    except:
        return error_page(request, _('Session malformed.'))

    # TODO: The user asks a logout, we should perform before knowing if the IdP can handle
    # Except if we want to manage mutliple logout with multiple IdP

    # If not defined in the metadata, put ANY to let lasso do its job from metadata
    if not p.identity_provider.enable_http_method_for_slo_request:
        try:
            logout.initRequest(None, lasso.HTTP_METHOD_ANY)
        except lasso.Error, error:
            localLogout(request)
        if logout.msgBody:
            logout.buildRequestMsg()
            # TODO: Client cert
            client_cert = None
            try:
                soap_answer = soap_call(logout.msgUrl, logout.msgBody, client_cert = client_cert)
            except SOAPException:
                localLogout(request)
            return slo_return(request, logout, soap_answer)
        else:
            session_index = get_session_index(request)
            if session_index:
                logout.request.sessionIndex = session_index
            logout.buildRequestMsg()
            #auth_logout(request)
            return HttpResponseRedirect(logout.msgUrl)
    # Else, taken from config
    if p.identity_provider.http_method_for_slo_request == lasso.HTTP_METHOD_REDIRECT:
        try:
            logout.initRequest(None, lasso.HTTP_METHOD_REDIRECT)
        except lasso.Error, error:
            localLogout(request)
        session_index = get_session_index(request)
        if session_index:
            logout.request.sessionIndex = session_index
        logout.buildRequestMsg()
        #auth_logout(request)
        return HttpResponseRedirect(logout.msgUrl)
    if p.identity_provider.http_method_for_slo_request == lasso.HTTP_METHOD_SOAP:
        try:
           logout.initRequest(None, lasso.HTTP_METHOD_SOAP)
        except lasso.Error, error:
            localLogout(request)
        logout.buildRequestMsg()
        # TODO: Client cert
        client_cert = None
        try:
            soap_answer = soap_call(logout.msgUrl, logout.msgBody, client_cert = client_cert)
        except SOAPException:
            localLogout(request)
        return slo_return(request, logout, soap_answer)
    return error_page(request, _('Unknown HTTP method.'))

def localLogout(request):
    remove_liberty_session_sp(request)
    auth_logout(request)
    return error_page(request, _('Could not send logout request to the identity provider.\n Only local logout performed.'))

###
 # singleLogoutReturn
 # @request
 #
 # Response from Redirect
 # Single Logout SOAP IdP initiated
 ###
def singleLogoutReturn(request):
    if not is_sp_configured():
        return error_page(request, _('Service provider not configured'))
    server = build_service_provider(request)
    if not server:
        error_page(request, _('Service provider not configured'))
    query = get_saml2_query_request(request)
    if not query:
        return error_page(request, _('SLO/Redirect: Unable to handle Single Logout by Redirect without request'))
    logout = lasso.Logout(server)
    load_session(request, logout)
    return slo_return(request, logout, query)

###
 # slo_return
 # @request
 # @logout
 # @message
 #
 # Post-response processing
 ###
def slo_return(request, logout, message):
    s = get_service_provider_settings()
    if not s:
        return error_page(request, _('Service provider not configured'))
    try:
        logout.processResponseMsg(message)
    except lasso.Error, error:
        return error_page(request, _('Could not send logout request to the identity provider.\n Only local logout performed.'))
    if logout.isSessionDirty:
        if logout.session:
            save_session(request, logout)
        else:
            delete_session(request)
    remove_liberty_session_sp(request)
    auth_logout(request)
    try:
        if s.back_url:
            return HttpResponseRedirect(s.back_url)
    except:
        pass
    return HttpResponseRedirect('/')

###
 # singleLogoutSOAP
 # @request
 #
 # Single Logout SOAP IdP initiated
 ###
@csrf_exempt
def singleLogoutSOAP(request):
    try:
        soap_message = get_soap_message(request)
    except:
        logging.warning(_('SLO/SOAP: Bad SOAP message'))
        return
    if not soap_message:
        logging.warning(_('SLO/SOAP: Bad SOAP message'))
        return

#        response = get_response()
#        response.set_content_type('text/xml')
#        session_index = None

    request_type = lasso.getRequestTypeFromSoapMsg(soap_message)
    if request_type != lasso.REQUEST_TYPE_LOGOUT:
        logging.warning(_('SLO/SOAP: SOAP message is not a slo message'))
        return

    if not is_sp_configured():
        logging.warning(_('SLO/SOAP: Service provider not configured'))
        return
        return error_page(request, _('Service provider not configured'))
    server = build_service_provider(request)
    if not server:
        logging.warning(_('SLO/SOAP: Service provider not configured'))
        return
    logout = lasso.Logout(server)

    try:
        logout.processRequestMsg(soap_message)
    except lasso.Error, error:
        handled_errors = (lasso.PROFILE_ERROR_MISSING_REMOTE_PROVIDERID,
                          lasso.DS_ERROR_INVALID_SIGNATURE,
                          lasso.DS_ERROR_SIGNATURE_NOT_FOUND)
        if error[0] in handled_errors:
            logging.warning(_('SLO/SOAP: Error while processing request %s' % error[1]))
            return
        else:
            logging.warning(_('SLO/SOAP: Unknown error while processing request'))
            return

    # Look for a session index
    try:
        session_index = logout.request.sessionIndex
    except:
        pass

    fed = lookup_federation_by_name_identifier(logout)
    if not fed:
        logging.warning(_('SLO/SOAP: Error while processing request %s' % error[1]))
        return

    session = None
    if session_index:
#        # Map session.id to session.index
#        for x in get_session_manager().values():
#            if logout.remoteProviderId is x.proxied_idp:
#                if x._proxy_session_index == session_index:
#                   session = x
#            else:
#                if x.get_session_index() == session_index:
#                    session = x
        # TODO: WARNING: A user can be logged without a federation!
        try:
            session = LibertySessionSP.objects.get(federation=fed, session_index=session_index)
        except:
            pass
#    else:
#        # No session index take the last session with the same name identifier
#        name_identifier = logout.nameIdentifier.content
#        for session_candidate in get_session_manager().values():
#            if name_identifier in (session_candidate.name_identifiers or []):
#                session = session_candidate
        try:
            session = LibertySessionSP.objects.get(federation=fed)
        except:
            # no session, build straight failure answer
           pass
    if session:
        q = LibertySessionDump.objects.filter(django_session_key = session.django_session_key)
        if not q:
            logging.warning(_('SLO/SOAP: No session dump for this session'))
            finishSingleLogoutSOAP(logout)
        logging.warning('SLO/SOAP from %s, for session index %s and session %s' % (logout.remoteProviderId, session_index, session.id))
        logout.setSessionFromDump(q[0].session_dump)
    else:
        logging.warning(_('SLO/SOAP: No Liberty session found'))
        finishSingleLogoutSOAP(logout)
#    authentic.identities.get_store().load_identities()
#    try:
#       identity = authentic.identities.get_store().get_identity(session.user)
#    except KeyError:
#        pass
#    else:
#        if identity.lasso_dump:
#            logout.setIdentityFromDump(identity.lasso_dump)
#    if session.proxied_idp:
#        self.proxy_slo_soap(session, identity)
#        logout.setSessionFromDump(session.lasso_session_dump)
    try:
        logout.validateRequest()
    except lasso.Error, error:
        handled_errors = (lasso.PROFILE_ERROR_MISSING_REMOTE_PROVIDERID,
                          lasso.DS_ERROR_INVALID_SIGNATURE,
                          lasso.DS_ERROR_SIGNATURE_NOT_FOUND,
                          lasso.LOGOUT_ERROR_UNSUPPORTED_PROFILE,
                          lasso.LOGOUT_ERROR_FEDERATION_NOT_FOUND,
                          lasso.PROFILE_ERROR_FEDERATION_NOT_FOUND,
                          lasso.PROFILE_ERROR_SESSION_NOT_FOUND)
        if error[0] in handled_errors:
            logging.warning(_('SLO/SOAP: Error while validating request: %s' % error[1]))
            finishSingleLogoutSOAP(logout)
        else:
            import sys
            logging.warning(_('SLO/SOAP: Unknown error while validating request%s' % sys.exc_info()[0]))
            finishSingleLogoutSOAP(logout)
    else:
        django_session_key = session.django_session_key
        session.delete()
        q[0].delete()
        from django.contrib.sessions.models import Session
        try:
            ss = Session.objects.all()
            for s in ss:
                if s.session_key == django_session_key:
                    session_django = s
        except:
            import sys
            logging.warning(_('SLO/SOAP: Unable to log django session: %s' % sys.exc_info()[0]))
            finishSingleLogoutSOAP(logout)
        try:
            session_django.delete()
        except:
            import sys
            logging.warning(_('SLO/SOAP: Unable to log django session: %s' % sys.exc_info()[0]))
            finishSingleLogoutSOAP(logout)
    finishSingleLogoutSOAP(logout)

def finishSingleLogoutSOAP(logout):
    logout.buildResponseMsg()
    return logout.msgBody

###
 # singleLogout
 # @request
 #
 # Single Logout Redirect IdP initiated
 ###
def singleLogout(request):

    if not is_sp_configured():
        return error_page(request, _('SLO/Redirect: Service provider not configured'))

    query = get_saml2_query_request(request)
    if not query:
        return error_page(request, _('SLO/Redirect: Unable to handle Single Logout by Redirect without request'))

    server = build_service_provider(request)
    if not server:
        return error_page(_('SLO/Redirect: Service provider not configured'))

    logout = lasso.Logout(server)
    try:
        logout.processRequestMsg(query)
    except lasso.Error, error:
        if error[0] == lasso.DS_ERROR_INVALID_SIGNATURE:
            logging.warning(_('SLO/Redirect from %s: Invalid Signature' % logout.remoteProviderId))
        else:
            import sys
            return error_page(_('SLO/Redirect from %s: Unknown error%s' % (logout.remoteProviderId, sys.exc_info()[0])))
        return slo_return_response(logout)

    logging.warning(_('SLO/Redirect from %s:' % logout.remoteProviderId))

    load_session(request, logout)

    try:
        logout.validateRequest()
    except lasso.Error, error:
        handled_errors = (lasso.PROFILE_ERROR_MISSING_REMOTE_PROVIDERID,
                          lasso.DS_ERROR_INVALID_SIGNATURE,
                          lasso.DS_ERROR_SIGNATURE_NOT_FOUND,
                          lasso.LOGOUT_ERROR_UNSUPPORTED_PROFILE,
                          lasso.LOGOUT_ERROR_FEDERATION_NOT_FOUND,
                          lasso.PROFILE_ERROR_FEDERATION_NOT_FOUND,
                          lasso.PROFILE_ERROR_SESSION_NOT_FOUND)
        if error[0] in handled_errors:
            #print 'SLO/Redirect: Error while validating request: %s' % error[1]
            logging.warning(_('SLO/Redirect: Error while validating request: %s' % error[1]))
            slo_return_response(logout)
        else:
            import sys
            #print 'SLO/Redirect: Unknown error while validating request%s' % sys.exc_info()[0]
            logging.warning(_('SLO/Redirect: Unknown error while validating request%s' % sys.exc_info()[0]))
            slo_return_response(logout)

    if logout.isSessionDirty:
        if logout.session:
            save_session(request, logout)
        else:
            delete_session(request)
    remove_liberty_session_sp(request)
    auth_logout(request)

    # TODO: we cannot call slo_return_response, else django raise an error due an httpresponse return missing
    try:
        logout.buildResponseMsg()
    except lasso.Error, error:
        if error[0] == lasso.PROFILE_ERROR_UNKNOWN_PROFILE_URL:
            # metadata didn't contain logout return url, stay here.
            return error_page(_('SLO/Response from %s: Error unknown profile URL' % remoteProviderId))
        elif error[0] == lasso.SERVER_ERROR_PROVIDER_NOT_FOUND:
            return error_page(_('SLO/Response from %s: Provider not found' % remoteProviderId))
        else:
            import sys
            return error_page(_('SLO/Redirect from %s: Unknown error%s' % (logout.remoteProviderId, sys.exc_info()[0])))
    else:
        return HttpResponseRedirect(logout.msgUrl)

def slo_return_response(logout):
    try:
        logout.buildResponseMsg()
    except lasso.Error, error:
        if error[0] == lasso.PROFILE_ERROR_UNKNOWN_PROFILE_URL:
            # metadata didn't contain logout return url, stay here.
            return error_page(_('SLO/Response from %s: Error unknown profile URL' % remoteProviderId))
        elif error[0] == lasso.SERVER_ERROR_PROVIDER_NOT_FOUND:
            return error_page(_('SLO/Response from %s: Provider not found' % remoteProviderId))
        else:
            import sys
            return error_page(_('SLO/Redirect from %s: Unknown error%s' % (logout.remoteProviderId, sys.exc_info()[0])))
    else:
        return HttpResponseRedirect(logout.msgUrl)

###
 # federationTermination
 # @request
 # @method
 # @entity_id
 #
 # Name Identifier Management
 # Federation termination: request from user interface
 # Profile supported: Redirect, SOAP
 # For response, if the requester uses a (a)synchronous binding, the responder uses the same.
 # Else, the grabs the preferred method from the metadata.
 # By default we do not break the session.
 # TODO: Define in admin a parameter to indicate if the federation termination implies a local logout (IDP and SP initiated)
 # TODO: Clean tables of all dumps about this user
 ###
def federationTermination(request, entity_id):
    if not is_sp_configured():
        return error_page(request, _('Service provider not configured'))
    if not entity_id:
        return error_page(request, _('No provider for defederation'))
    if request.user.is_anonymous():
        return error_page(request, _('Unable to defederate a not logged user!'))
    server = build_service_provider(request)
    if not server:
        error_page(request, _('Service provider not configured'))
    # Lookup for the Identity provider
    try:
        p = LibertyProvider.objects.get(entity_id=entity_id)
    except:
        return error_page(request, _('No such identity provider.'))
    manage = lasso.NameIdManagement(server)
    load_session(request, manage)
    load_federation(request, manage)
    fed = lookup_federation_by_user(request.user, p.entity_id)
    if not fed:
        return error_page(request, _('Not a valid federation'))
    # The user asks a defederation, we perform without knowing if the IdP can handle
    fed.delete()
    # If not defined in the metadata, put ANY to let lasso do its job from metadata
    if not p.identity_provider.enable_http_method_for_defederation_request:
        try:
            manage.initRequest(entity_id, None, lasso.HTTP_METHOD_ANY)
        except lasso.Error, error:
            return error_page(request, _('fedTerm/SP: Unable to init defederation request'))
        if manage.msgBody:
            manage.buildRequestMsg()
            # TODO: Client cert
            client_cert = None
            try:
                soap_answer = soap_call(manage.msgUrl, manage.msgBody, client_cert = client_cert)
            except SOAPException:
                return error_page(request, _('fedTerm/SOAP SP: Unable to perform SOAP defederation request'))
            return manage_name_id_return(request, manage, soap_answer)
        else:
            manage.buildRequestMsg()
            save_manage(request, manage)
            return HttpResponseRedirect(manage.msgUrl)
    # Else, taken from config
    if p.identity_provider.http_method_for_defederation_request == lasso.HTTP_METHOD_REDIRECT:
        try:
            manage.initRequest(entity_id, None, lasso.HTTP_METHOD_REDIRECT)
        except lasso.Error, error:
            return error_page(request, _('fedTerm/Redirect SP: Unable to init defederation request'))
        manage.buildRequestMsg()
        save_manage(request, manage)
        return HttpResponseRedirect(manage.msgUrl)
    if p.identity_provider.http_method_for_defederation_request == lasso.HTTP_METHOD_SOAP:
        try:
           manage.initRequest(entity_id, None, lasso.HTTP_METHOD_SOAP)
        except lasso.Error, error:
            return error_page(request, _('fedTerm/SOAP SP: Unable to init defederation request'))
        manage.buildRequestMsg()
        # TODO: Client cert
        client_cert = None
        try:
            soap_answer = soap_call(manage.msgUrl, manage.msgBody, client_cert = client_cert)
        except SOAPException:
            return error_page(request, _('fedTerm/SOAP SP: Unable to perform SOAP defederation request'))
        return manage_name_id_return(request, manage, soap_answer)
    return error_page(request, _('Unknown HTTP method.'))

###
 # manageNameIdReturn
 # @request
 #
 # Federation termination: response from Redirect SP initiated
 ###
def manageNameIdReturn(request):
    server = build_service_provider(request)
    if not server:
        error_page(request, _('Service provider not configured'))
    manage_dump = get_manage_dump(request)
    manage = None
    if manage_dump and manage_dump.count()>1:
        for md in manage_dump:
            md.delete()
        error_page(request, _('Error managing manage dump'))
    elif manage_dump:
        manage = lasso.NameIdManagement.newFromDump(server, manage_dump[0].manage_dump)
        manage_dump.delete()
    else:
        manage = lasso.NameIdManagement(server)
    if not manage:
        return error_page(request, _('Defederation failed'))
    load_federation(request, manage)
    message = get_saml2_request_message(request)
    return manage_name_id_return(request, manage, message)

###
 # manage_name_id_return
 # @request
 # @logout
 # @message
 #
 # Post-response processing
 ###
def manage_name_id_return(request, manage, message):
    try:
        manage.processResponseMsg(message)
    except lasso.Error, error:
        return error_page(request, _('Defederation failed'))
    else:
        if manage.isIdentityDirty:
            if manage.identity:
                save_federation(request, manage)
    return redirect_to_target(request)

###
 # manageNameIdSOAP
 # @request
 #
 # Federation termination: request from SOAP IdP initiated
 ###
def manageNameIdSOAP(request):
    return error_page(request, _('manageNameIdSOAP'))

###
 # manageNameIdSOAP
 # @request
 #
 # Federation termination: request from Redirect IdP initiated
 ###
def manageNameId(request):
    return error_page(request, _('manageNameId'))

#############################################
# Helper functions 
#############################################

def check_response_id(login):
    try:
        session_ext = ExtendDjangoSession.objects.get(saml_request_id=login.response.inResponseTo)
    except ExtendDjangoSession.DoesNotExist:
        return False
    return True

def build_service_provider(request):
    sp = create_saml2_sp_server(request, reverse(metadata))
    if not sp:
        return None
    providers_list = get_idp_list()
    if not providers_list:
        return None
    for p in providers_list:
        add_idp_to_sp(request, sp, p)
    return sp

def add_idp_to_sp(request, sp, p):
    try:
         sp.addProviderFromBuffer(
             lasso.PROVIDER_ROLE_IDP,
             p.metadata.read(),
             p.public_key.read(),
             None)
    except:
        logging.error(_('Unable to load provider %r') % p.entity_id)
        pass
