import datetime, time
import logging

import lasso
from django.conf import settings
from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import *
from django.views.decorators.csrf import *
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.contrib.auth import get_user
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext as _
from authentic2.saml.common import *
from authentic2.saml.models import *
from authentic2.authsaml2.utils import *
from authentic2.authsaml2.backends import *
import signals

__logout_redirection_timeout = getattr(settings, 'IDP_LOGOUT_TIMEOUT', 600)

'''SAMLv2 SP implementation'''

logger = logging.getLogger('authentic.auth.saml2')

def metadata(request):
    '''Endpoint to retrieve the metadata file'''
    return HttpResponse(get_metadata(request, request.path),
            mimetype='text/xml')

###
 # sso
 # @request
 # @entity_id: Provider ID to request
 #
 # Single SignOn request initiated from SP UI
 # Binding supported: Redirect
 ###
def sso(request, entity_id=None, is_passive=None, force_authn=None):
    '''Django view initiating an AuthnRequesst toward an identity provider.

       Keyword arguments:
       entity_id -- the SAMLv2 entity id identifier targeted by the
       AuthnRequest, it should be resolvable to a metadata document.
       is_passive -- whether to let the identity provider passively, i.e.
       without user interaction, authenticate the user.
       force_authn -- whether to ask the identity provider to authenticate the
       user even if it is already authenticated.
    '''
    s = get_service_provider_settings()
    if not s:
        return error_page(request, _('SSO/Artifact: Service provider not configured'))
    # 1. Save the target page
    session_ext = register_next_target(request)
    if not session_ext:
        return error_page(request, _('SSO/Artifact: Error handling session'))
    # 2. Init the server object
    server = build_service_provider(request)
    if not server:
        return error_page(request, _('SSO/Artifact: Service provider not configured'))
    # 3. Define the provider or ask the user
    if not entity_id:
        providers_list = get_idp_list()
        if not providers_list:
            return error_page(request, 'SSO/Artifact: Service provider not configured')
        if providers_list.count() == 1:
            p = providers_list[0]
        else:
            return render_to_response('auth/saml2/idp_select.html',
                    {'providers_list': providers_list},
                    context_instance=RequestContext(request))
    else:
        p = load_provider(request, entity_id, server=server, sp_or_idp='idp')
        if not p:
            return error_page(request, 'SSO/Artifact: The provider does not exist')
    # 4. Build authn request
    login = lasso.Login(server)
    if not login:
        return error_page(request, _('SSO/Artifact: Unable to create Login object'))
    # Only redirect is necessary for the authnrequest
    try:
        login.initAuthnRequest(p.entity_id, lasso.HTTP_METHOD_REDIRECT)
    except lasso.Error, error:
        return error_page(request, _('SSO/SP UI: %s') %lasso.strError(error[0]))

    # 5. IdP configuration
    if s.activate_default_sp_policy:
        if s.no_nameid_policy:
            login.request.nameIDPolicy = None
        else:
            login.request.nameIDPolicy.format = NAME_ID_FORMATS[s.requested_name_id_format]['samlv2']
            login.request.nameIDPolicy.allowCreate = s.allow_create
            #login.request.nameIDPolicy.spNameQualifier = "https://shibidp.mik.lan/idp/shibboleth"
        if s.enable_binding_for_sso_response:
            login.request.protocolBinding = s.binding_for_sso_response
        login.request.forceAuthn = s.want_force_authn_request
        login.request.isPassive = s.want_is_passive_authn_request
        login.request.consent = s.user_consent
    else:
        if p.identity_provider.no_nameid_policy:
            login.request.nameIDPolicy = None
        else:
            login.request.nameIDPolicy.format = NAME_ID_FORMATS[p.identity_provider.requested_name_id_format]['samlv2']
            login.request.nameIDPolicy.allowCreate = p.identity_provider.allow_create
            #login.request.nameIDPolicy.spNameQualifier = "https://shibidp.mik.lan/idp/shibboleth"
        if p.identity_provider.enable_binding_for_sso_response:
            login.request.protocolBinding = p.identity_provider.binding_for_sso_response
        if force_authn is None:
            force_authn = p.identity_provider.want_force_authn_request
        login.request.forceAuthn = force_authn
        if is_passive is None:
            is_passive = p.identity_provider.want_is_passive_authn_request
        login.request.isPassive = is_passive
        login.request.consent = p.identity_provider.user_consent

    try:
        login.buildAuthnRequestMsg()
    except lasso.Error, error:
        return error_page(request, _('SSO/SP UI: %s') %lasso.strError(error[0]))
    # 6. Save the request ID (association with the target page)
    session_ext.saml_request_id = login.request.iD
    session_ext.save()
    # 7. Redirect the user
    import sys
    print >> sys.stderr, login.request.dump()

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
        return error_page(request, _('SSO/Artifact: Service provider not configured'))

    login = lasso.Login(server)
    if not login:
        return error_page(request, _('SSO/Artifact: Unable to create Login object'))

    message = get_saml2_request_message(request)

    try:
        if request.method == 'GET':
            login.initRequest(message, lasso.HTTP_METHOD_ARTIFACT_GET)
        else:
            login.initRequest(message, lasso.HTTP_METHOD_ARTIFACT_POST)
    except lasso.Error, error:
        return error_page(request, _('SSO/Artifact: %s') %lasso.strError(error[0]))

    try:
        login.buildRequestMsg()
    except lasso.Error, error:
        return error_page(request, _('SSO/Artifact: %s') %lasso.strError(error[0]))

    import sys
    print >> sys.stderr, login.request.dump()

    # TODO: Client certificate
    client_cert = None
    try:
        soap_answer = soap_call(login.msgUrl, login.msgBody, client_cert = client_cert)
    except Exception, e:
        logger.exception('SSO: Failure to communicate with artifact resolver %r' % login.msgUrl, e)
        return error_page(request, _('SSO/Artifact: Failure to communicate with identity provider'))
    if not soap_answer:
        logger.error('SSO: Artifact resolver at %r returned an empty response' % login.msgUrl)
        return error_page(request, _('SSO/Artifact: Failure to communicate with identity provider'))

    # If connexion over HTTPS, do not check signature?!
    if login.msgUrl.startswith('https'):
        login.setSignatureVerifyHint(lasso.PROFILE_SIGNATURE_HINT_FORBID)

    try:
        login.processResponseMsg(soap_answer)
    except lasso.Error, error:
        print >> sys.stderr, login.response.dump()
        return error_page(request, _('SSO/Artifact: %s') %lasso.strError(error[0]))

    # TODO: Relay State

    return sso_after_response(request, login)

@csrf_exempt
def singleSignOnPost(request):
    server = build_service_provider(request)
    if not server:
        return error_page(request, _('SSO/Post: Service provider not configured'))

    login = lasso.Login(server)
    if not login:
        return error_page(request, _('SSO/Post: Unable to create Login object'))

    # TODO: check messages = get_saml2_request_message(request)

    # Binding POST
    message = get_saml2_post_response(request)
    if not message:
        return error_page(request, _('SSO/Post: No message given.'))

    # Binding REDIRECT
    # According to: saml-profiles-2.0-os
    # The HTTP Redirect binding MUST NOT be used, as the response will typically exceed the URL length permitted by most user agents.
    # if not message:
    #    message = request.META.get('QUERY_STRING', '')

    try:
        login.processAuthnResponseMsg(message)
    except lasso.Error, error:
        return error_page(request, _('SSO/Post: %s') %lasso.strError(error[0]))

    return sso_after_response(request, login)

###
 # sso_after_response
 # @request
 # @login
 # @relay_state
 #
 # Post-authnrequest processing
 # TODO: Proxying
 ###
def sso_after_response(request, login, relay_state = None):
    # If there is no inResponseTo: IDP initiated
    # else, check that the response id is the same
    irt = None
    try:
        irt = login.response.assertion[0].subject.subjectConfirmation.subjectConfirmationData.inResponseTo
    except:
        return error_page(request, _('SSO/sso_after_response: No Response ID'))

    if irt and not check_response_id(login):
        return error_page(request, _('SSO/sso_after_response: Request and Response ID do not match'))

    #TODO: Register assertion and check for replay
    assertion = login.response.assertion[0]
    if not assertion:
        return error_page(request, _('SSO/sso_after_response: Assertion missing'))

    # Check: Check that the url is the same as in the assertion
    try:
        if assertion.subject.subjectConfirmation.subjectConfirmationData.recipient != \
                request.build_absolute_uri().partition('?')[0]:
            return error_page(request, _('SSO/sso_after_response: SubjectConfirmation Recipient Mismatch'))
    except:
            return error_page(request, _('SSO/sso_after_response: Errot checking SubjectConfirmation Recipient'))

    # Check: SubjectConfirmation
    try:
        if assertion.subject.subjectConfirmation.method != \
                'urn:oasis:names:tc:SAML:2.0:cm:bearer':
            return error_page(request, _('SSO/sso_after_response: Unknown SubjectConfirmation Method'))
    except:
        return error_page(request, _('SSO/sso_after_response: Error checking SubjectConfirmation Method'))

    # Check: AudienceRestriction
    try:
        audience_ok = False
        for audience_restriction in assertion.conditions.audienceRestriction:
            if audience_restriction.audience != login.server.providerId:
                return error_page(request, _('SSO/sso_after_response: Incorrect AudienceRestriction'))
            audience_ok = True
        if not audience_ok:
            return error_page(request, _('SSO/sso_after_response: Incorrect AudienceRestriction'))
    except:
        return error_page(request, _('SSO/sso_after_response: Error checking AudienceRestriction'))

    # Check: notBefore, notOnOrAfter
    try:
        now = datetime.datetime.utcnow()
        not_before = assertion.subject.subjectConfirmation.subjectConfirmationData.notBefore
        not_on_or_after = assertion.subject.subjectConfirmation.subjectConfirmationData.notOnOrAfter
        # TODO: Make a smart parsing to not fail if the date is not as much precise
        if not_before and now < datetime.datetime.fromtimestamp(time.mktime(time.strptime(not_before,"%Y-%m-%dT%H:%M:%S.%fZ"))):
            return error_page(request, _('SSO/sso_after_response: Assertion received too early'))
        if not_on_or_after and now > datetime.datetime.fromtimestamp(time.mktime(time.strptime(not_on_or_after,"%Y-%m-%dT%H:%M:%S.%fZ"))):
            return error_page(request, _('SSO/sso_after_response: Assertion expired'))
    except:
        return error_page(request, _('SSO/sso_after_response: Error checking Assertion Time'))

    try:
        login.acceptSso()
    except lasso.Error, error:
        return error_page(request, _('SSO/sso_after_response: %s') %lasso.strError(error[0]))

    s = get_service_provider_settings()
    if not s:
        return error_page(request, _('Service provider not configured'))

    user = request.user
    if not request.user.is_anonymous():
        #TODO: If transient nameID and logged user, only logging
        if login.nameIdentifier.format == "urn:oasis:names:tc:SAML:2.0:nameid-format:transient":
            return error_page(request, _('Persistent account policy not yet implemented'))

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
        if login.nameIdentifier.format == \
            lasso.SAML2_NAME_IDENTIFIER_FORMAT_TRANSIENT:
            if s.handle_transient == 'AUTHSAML2_UNAUTH_TRANSIENT_ASK_AUTH':
                return error_page(request, _('Transient access policy not yet implemented'))
            if s.handle_transient == 'AUTHSAML2_UNAUTH_TRANSIENT_OPEN_SESSION':
                #TODO: Logging
                from backends import AuthSAML2Backend
                user = AuthSAML2Backend().create_user(nameId=login.nameIdentifier.content)
                key = request.session.session_key
                auth_login(request, user)
                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                save_session(request, login)
                return redirect_to_target(request)
            return error_page(request, _('Transient access policy: Configuration error'))

        if login.nameIdentifier.format == \
            lasso.SAML2_NAME_IDENTIFIER_FORMAT_PERSISTENT:
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
            if s.handle_persistent == 'AUTHSAML2_UNAUTH_PERSISTENT_ACCOUNT_LINKING_BY_AUTH':
                register_federation_in_progress(request,login.nameIdentifier.content)
                save_session(request, login)
                save_federation_temp(request, login)
                maintain_liberty_session_on_service_provider(request, login)
                return render_to_response('auth/saml2/account_linking.html',
                        context_instance=RequestContext(request))
            if s.handle_persistent == 'AUTHSAML2_UNAUTH_PERSISTENT_CREATE_USER_PSEUDONYMOUS':
                user = AuthSAML2Backend().create_user(nameId=login.nameIdentifier.content)
                key = request.session.session_key
                auth_login(request, user)
                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                save_session(request, login)
                maintain_liberty_session_on_service_provider(request, login)
                return redirect_to_target(request, key)
            return error_page(request, _('Persistent Account policy: Configuration error'))

        return error_page(request, _('Transient access policy: NameId format not supported'))
        #TODO: Relay state

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
                return error_page(request, _('SSO/finish_federation: Service provider not configured'))

            login = lasso.Login(server)
            if not login:
                return error_page(request, _('SSO/finish_federation: Unable to create Login object'))

            s = load_session(request, login)
            load_federation_temp(request, login)
            if not login.session:
                return error_page(request, _('SSO/finish_federation: Error loading session.'))
            login.nameIdentifier = login.session.getAssertions()[0].subject.nameID

            fed = add_federation(form.get_user(), login)
            if not fed:
                return error_page(request, _('SSO/finish_federation: Error adding new federation for this user'))
            key = request.session.session_key
            auth_login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            #s.delete()
            login.session.isDirty = True
            login.identity.isDirty = True
            save_session(request, login)
            save_federation(request, login)
            maintain_liberty_session_on_service_provider(request, login)
            return redirect_to_target(request, key)
        else:
            # TODO: Error: login failed: message and count 3 attemps
            return render_to_response('auth/saml2/account_linking.html',
                    context_instance=RequestContext(request))
    else:
        return error_page(request, _('SSO/finish_federation: Unable to perform federation'))

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
 # Single Logout Request from UI
 ###
def logout(request):
    if not is_sp_configured():
        return error_page(request, _('SLO/SP UI: Service provider not configured'))

    if request.user.is_anonymous():
        return error_page(request, _('SLO/SP UI: Unable to logout a not logged user!'))

    server = build_service_provider(request)
    if not server:
        return error_page(request, _('SLO/SP UI: Service provider not configured'))

    logout = lasso.Logout(server)
    if not logout:
        return error_page(request, _('SLO/SP UI: Unable to create Login object'))

    load_session(request, logout)

    # Lookup for the Identity provider from session
    q = LibertySessionDump.objects.filter(django_session_key = request.session.session_key)
    if not q:
        return error_page(request, _('SLO/SP UI: No session for global logout.'))
    try:
        pid = lasso.Session().newFromDump(q[0].session_dump).get_assertions().keys()[0]
        p = LibertyProvider.objects.get(entity_id=pid)
    except:
        return error_page(request, _('SLO/SP UI: Session malformed.'))

    # TODO: The user asks a logout, we should perform before knowing if the IdP can handle
    # Except if we want to manage mutliple logout with multiple IdP

    # TODO: Default SP policy configuration

    # If not defined in the metadata, put ANY to let lasso do its job from metadata
    if not p.identity_provider.enable_http_method_for_slo_request:
        try:
            logout.initRequest(None, lasso.HTTP_METHOD_ANY)
        except lasso.Error, error:
            localLogout(request, error)
        if not logout.msgBody:
            try:
                logout.buildRequestMsg()
            except lasso.Error, error:
                return localLogout(request, error)

            # TODO: Client cert
            client_cert = None
            try:
                soap_answer = soap_call(logout.msgUrl, logout.msgBody, client_cert = client_cert)
            except SOAPException:
                return localLogout(request, error)

            return slo_return(request, logout, soap_answer)

        else:
            session_index = get_session_index(request)
            if session_index:
                logout.request.sessionIndex = session_index

            try:
                logout.buildRequestMsg()
            except lasso.Error, error:
                return localLogout(request, error)

            return HttpResponseRedirect(logout.msgUrl)

    # Else, taken from config
    if p.identity_provider.http_method_for_slo_request == lasso.HTTP_METHOD_REDIRECT:
        try:
            logout.initRequest(None, lasso.HTTP_METHOD_REDIRECT)
        except lasso.Error, error:
            return localLogout(request, error)

        session_index = get_session_index(request)
        if session_index:
            logout.request.sessionIndex = session_index

        try:
            logout.buildRequestMsg()
        except lasso.Error, error:
            return localLogout(request, error)

        return HttpResponseRedirect(logout.msgUrl)

    if p.identity_provider.http_method_for_slo_request == lasso.HTTP_METHOD_SOAP:
        try:
           logout.initRequest(None, lasso.HTTP_METHOD_SOAP)
        except lasso.Error, error:
            return localLogout(request, error)

        try:
            logout.buildRequestMsg()
        except lasso.Error, error:
            return localLogout(request, error)

        # TODO: Client cert
        client_cert = None
        soap_answer = None
        try:
            soap_answer = soap_call(logout.msgUrl, logout.msgBody, client_cert = client_cert)
        except SOAPException, error:
            return localLogout(request, error)

        if not soap_answer:
            remove_liberty_session_sp(request)
            auth_logout(request)
            return error_page(request, _('SLO/SP UI: SOAP error -  Only local logout performed.'))

        return slo_return(request, logout, soap_answer)

    return error_page(request, _('SLO/SP UI: Unknown HTTP method.'))

def localLogout(request, error):
    remove_liberty_session_sp(request)
    auth_logout(request)
    if error.url:
        return error_page(request, _('SLO/SP UI: SOAP error with %s -  Only local logout performed.') %error.url)
    return error_page(request, _('SLO/SP UI: %s -  Only local logout performed.') %lasso.strError(error[0]))

###
 # singleLogoutReturn
 # @request
 #
 # Response from Redirect
 # Single Logout SOAP IdP initiated
 ###
def singleLogoutReturn(request):
    if not is_sp_configured():
        return error_page(request, _('SLO/SP Redirect: Service provider not configured'))

    server = build_service_provider(request)
    if not server:
        return error_page(request, _('SLO/SP Redirect: Service provider not configured'))

    query = get_saml2_query_request(request)
    if not query:
        return error_page(request, _('SLO/SP Redirect: Unable to handle Single Logout by Redirect without request'))

    logout = lasso.Logout(server)
    if not logout:
        return error_page(request, _('SLO/SP Redirect: Unable to create Login object'))

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
    try:
        logout.processResponseMsg(message)
    except lasso.Error, error:
        # Silent local logout
        return local_logout(request)
    if logout.isSessionDirty:
        if logout.session:
            save_session(request, logout)
        else:
            delete_session(request)
    remove_liberty_session_sp(request)
    return local_logout(request)

def local_logout(request):
        global __logout_redirection_timeout
        "Logs out the user and displays 'You are logged out' message."
        signals.auth_logout.send(sender = None, user = request.user)
        context = RequestContext(request)
        context['redir_timeout'] = __logout_redirection_timeout
        context['message'] = 'You are logged out'
        template = 'idp/logout.html'
        s = get_service_provider_settings()
        if not s or not s.back_url:
            context['next_page'] = '/'
        else:
            context['next_page'] = s.back_url
        auth_logout(request)
        return render_to_response(template, context_instance = context)

###
 # singleLogoutSOAP
 # @request
 #
 # Single Logout SOAP IdP initiated
 # TODO: Manage valid soap responses on error (else error 500)
 ###
@csrf_exempt
def singleLogoutSOAP(request):
    try:
        soap_message = get_soap_message(request)
    except:
        return http_response_bad_request('SLO/IdP SOAP: Bad SOAP message')

    if not soap_message:
        return http_response_bad_request('SLO/IdP SOAP: Bad SOAP message')

    request_type = lasso.getRequestTypeFromSoapMsg(soap_message)
    if request_type != lasso.REQUEST_TYPE_LOGOUT:
        return http_response_bad_request('SLO/IdP SOAP: SOAP message is not a slo message')

    if not is_sp_configured():
        return http_response_forbidden_request('SLO/IdP SOAP: Service provider not configured')

    server = build_service_provider(request)
    if not server:
        return http_response_forbidden_request('SLO/IdP SOAP: Service provider not configured')

    logout = lasso.Logout(server)
    if not logout:
        return http_response_forbidden_request('SLO/IdP SOAP: Unable to create Login object')

    try:
        logout.processRequestMsg(soap_message)
    except lasso.Error, error:
        message = 'SLO/IdP SOAP processRequestMsg: %s' %lasso.strError(error[0])
        return http_response_forbidden_request(message)

    # Look for a session index
    try:
        session_index = logout.request.sessionIndex
    except:
        pass

    fed = lookup_federation_by_name_identifier(logout)
    if not fed:
        return http_response_forbidden_request('SLO/IdP SOAP: Unable to find user')

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
            logger.warning('SLO/IdP SOAP: No session dump for this session')
            finishSingleLogoutSOAP(logout)
        logger.warning('SLO/IdP SOAP from %s, for session index %s and session %s' % (logout.remoteProviderId, session_index, session.id))
        logout.setSessionFromDump(q[0].session_dump.encode('utf8'))
    else:
        logger.warning('SLO/IdP SOAP: No Liberty session found')
        return finishSingleLogoutSOAP(logout)
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
        message = 'SLO/IdP SOAP validateRequest: %s' %lasso.strError(error[0])
        logger.warning(message)
        # We continue the process
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
        logger.warning('SLO/IdP SOAP: Unable to grab user session: %s' %sys.exc_info()[0])
        return finishSingleLogoutSOAP(logout)
    try:
        session_django.delete()
    except:
        import sys
        logger.warning('SLO/IdP SOAP: Unable to delete user session: %s' %sys.exc_info()[0])
        return finishSingleLogoutSOAP(logout)

    return finishSingleLogoutSOAP(logout)

def finishSingleLogoutSOAP(logout):
    try:
        logout.buildResponseMsg()
    except:
        logger.warning('SLO/IdP SOAP buildResponseMsg: %s' %lasso.strError(error[0]))
        return http_response_forbidden_request(message)

    django_response = HttpResponse()
    django_response.status_code = 200
    django_response.content_type = 'text/xml'
    django_response.content = logout.msgBody
    return django_response

###
 # singleLogout
 # @request
 #
 # Single Logout Redirect IdP initiated
 ###
def singleLogout(request):
    if not is_sp_configured():
        return http_response_forbidden_request('SLO/IdP Redirect: Service provider not configured')

    query = get_saml2_query_request(request)
    if not query:
        return http_response_forbidden_request('SLO/IdP Redirect: Unable to handle Single Logout by Redirect without request')

    server = build_service_provider(request)
    if not server:
        return http_response_forbidden_request('SLO/IdP Redirect: Service provider not configured')

    logout = lasso.Logout(server)
    try:
        logout.processRequestMsg(query)
    except lasso.Error, error:
        logger.warning('SLO/IdP Redirect: %s' %lasso.strError(error[0]))
        return slo_return_response(logout)

    logger.warning('SLO/IdP Redirect from %s:' % logout.remoteProviderId)

    load_session(request, logout)

    try:
        logout.validateRequest()
    except lasso.Error, error:
        logger.warning('SLO/IdP Redirect: %s' %lasso.strError(error[0]))
        return slo_return_response(logout)

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
        return http_response_forbidden_request('SLO/IdP Redirect: %s') %lasso.strError(error[0])
    else:
        return HttpResponseRedirect(logout.msgUrl)

def slo_return_response(logout):
    try:
        logout.buildResponseMsg()
    except lasso.Error, error:
        return http_response_forbidden_request('SLO/slo_return_response: %s') %lasso.strError(error[0])
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
 # TODO: Define in admin a parameter to indicate if the federation termination implies a local logout (IDP and SP initiated) - Should not logout.
 # TODO: Clean tables of all dumps about this user
 ###
def federationTermination(request, entity_id):
    if not is_sp_configured():
        return error_page(request, _('fedTerm/SP UI: Service provider not configured'))

    if not entity_id:
        return error_page(request, _('fedTerm/SP UI: No provider for defederation'))

    if request.user.is_anonymous():
        return error_page(request, _('fedTerm/SP UI: Unable to defederate a not logged user!'))

    server = build_service_provider(request)
    if not server:
        error_page(request, _('fedTerm/SP UI: Service provider not configured'))

    # Lookup for the Identity provider
    try:
        p = LibertyProvider.objects.get(entity_id=entity_id)
    except:
        return error_page(request, _('fedTerm/SP UI: No such identity provider.'))

    manage = lasso.NameIdManagement(server)

    load_session(request, manage)
    load_federation(request, manage)
    fed = lookup_federation_by_user(request.user, p.entity_id)
    if not fed:
        return error_page(request, _('fedTerm/SP UI: Not a valid federation'))

    # The user asks a defederation, we perform without knowing if the IdP can handle
    fed.delete()
    # If not defined in the metadata, put ANY to let lasso do its job from metadata

    if not p.identity_provider.enable_http_method_for_defederation_request:
        try:
            manage.initRequest(entity_id, None, lasso.HTTP_METHOD_ANY)
        except lasso.Error, error:
            return error_page(request, _('fedTerm/SP UI: %s') %lasso.strError(error[0]))

        if manage.msgBody:
            try:
                manage.buildRequestMsg()
            except lasso.Error, error:
                return error_page(request, _('fedTerm/SP SOAP: %s') %lasso.strError(error[0]))
            # TODO: Client cert
            client_cert = None
            try:
                soap_answer = soap_call(manage.msgUrl, manage.msgBody, client_cert = client_cert)
            except SOAPException:
                return error_page(request, _('fedTerm/SP SOAP: Unable to perform SOAP defederation request'))
            return manage_name_id_return(request, manage, soap_answer)
        else:
            try:
                manage.buildRequestMsg()
            except lasso.Error, error:
                return error_page(request, _('fedTerm/SP Redirect: %s') %lasso.strError(error[0]))
            save_manage(request, manage)
            return HttpResponseRedirect(manage.msgUrl)

    # Else, taken from config
    if p.identity_provider.http_method_for_defederation_request == lasso.HTTP_METHOD_SOAP:
        try:
            manage.initRequest(entity_id, None, lasso.HTTP_METHOD_SOAP)
            manage.buildRequestMsg()
        except lasso.Error, error:
            return error_page(request, _('fedTerm/SP SOAP: %s') %lasso.strError(error[0]))
        # TODO: Client cert
        client_cert = None
        try:
            soap_answer = soap_call(manage.msgUrl, manage.msgBody, client_cert = client_cert)
        except SOAPException:
            return error_page(request, _('fedTerm/SP SOAP: Unable to perform SOAP defederation request'))
        return manage_name_id_return(request, manage, soap_answer)

    if p.identity_provider.http_method_for_defederation_request == lasso.HTTP_METHOD_REDIRECT:
        try:
            manage.initRequest(entity_id, None, lasso.HTTP_METHOD_REDIRECT)
            manage.buildRequestMsg()
        except lasso.Error, error:
            return error_page(request, _('fedTerm/SP Redirect: %s') %lasso.strError(error[0]))
        save_manage(request, manage)
        return HttpResponseRedirect(manage.msgUrl)

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
        error_page(request, _('fedTerm/SP Redirect: Service provider not configured'))

    manage_dump = get_manage_dump(request)
    manage = None
    if manage_dump and manage_dump.count()>1:
        for md in manage_dump:
            md.delete()
        error_page(request, _('fedTerm/SP Redirect: Error managing manage dump'))
    elif manage_dump:
        manage = lasso.NameIdManagement.newFromDump(server, manage_dump[0].manage_dump)
        manage_dump.delete()
    else:
        manage = lasso.NameIdManagement(server)

    if not manage:
        return error_page(request, _('fedTerm/SP Redirect: Defederation failed'))

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
        return error_page(request, _('fedTerm/manage_name_id_return: %s') %lasso.strError(error[0]))
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
 # TODO: Manage valid soap responses on error (else error 500)
 ###
@csrf_exempt
def manageNameIdSOAP(request):
    try:
        soap_message = get_soap_message(request)
    except:
        return http_response_bad_request('fedTerm/IdP SOAP: Bad SOAP message')
    if not soap_message:
        return http_response_bad_request('fedTerm/IdP SOAP: Bad SOAP message')

    request_type = lasso.getRequestTypeFromSoapMsg(soap_message)
    if request_type != lasso.REQUEST_TYPE_NAME_ID_MANAGEMENT:
        return http_response_bad_request('fedTerm/IdP SOAP: SOAP message is not a slo message')

    if not is_sp_configured():
        return http_response_forbidden_request('fedTerm/IdP SOAP: Service provider not configured')

    server = build_service_provider(request)
    if not server:
        return http_response_forbidden_request('fedTerm/IdP SOAP: Service provider not configured')

    manage = lasso.NameIdManagement(server)
    if not manage:
        return http_response_forbidden_request('fedTerm/IdP SOAP: Unable to create Login object')

    try:
        manage.processRequestMsg(soap_message)
    except lasso.Error, error:
        message = 'fedTerm/IdP SOAP: %s' %lasso.strError(error[0])
        return http_response_forbidden_request(message)

    fed = lookup_federation_by_name_identifier(manage)
    load_federation(request, manage, fed.user)
    try:
        manage.validateRequest()
    except lasso.Error, error:
        message = 'fedTerm/IdP SOAP: %s' %lasso.strError(error[0])
        return http_response_forbidden_request(message)

    fed.delete()

    try:
        manage.buildResponseMsg()
    except:
        message = 'fedTerm/IdP SOAP: %s' %lasso.strError(error[0])
        return http_response_forbidden_request(message)

    django_response = HttpResponse()
    django_response.status_code = 200
    django_response.content_type = 'text/xml'
    django_response.content = manage.msgBody
    return django_response

###
 # manageNameId
 # @request
 #
 # Federation termination: request from Redirect IdP initiated
 ###
def manageNameId(request):
    if not is_sp_configured():
        return http_response_forbidden_request('fedTerm/IdP Redirect: Service provider not configured')

    query = get_saml2_query_request(request)
    if not query:
        return http_response_forbidden_request('fedTerm/IdP Redirect: Unable to handle Single Logout by Redirect without request')

    server = build_service_provider(request)
    if not server:
        return http_response_forbidden_request('fedTerm/IdP Redirect: Service provider not configured')

    manage = lasso.NameIdManagement(server)
    if not manage:
        return http_response_forbidden_request('fedTerm/IdP Redirect: Unable to create Login object')

    try:
        manage.processRequestMsg(query)
    except lasso.Error, error:
        message = 'fedTerm/IdP Redirect: %s' %lasso.strError(error[0])
        return http_response_forbidden_request(message)

    fed = lookup_federation_by_name_identifier(manage)
    load_federation(request, manage, fed.user)
    try:
        manage.validateRequest()
    except lasso.Error, error:
        logger.warning('fedTerm/IdP Redirect: Unable to validate request')
        return

    fed.delete()

    try:
        manage.buildResponseMsg()
    except:
        message = 'fedTerm/IdP Redirect: %s' %lasso.strError(error[0])
        return http_response_forbidden_request(message)

    return HttpResponseRedirect(manage.msgUrl)

#############################################
# Helper functions 
#############################################

metadata_map = (('AssertionConsumerService', lasso.SAML2_METADATA_BINDING_ARTIFACT , '/singleSignOnArtifact'),
    ('AssertionConsumerService', lasso.SAML2_METADATA_BINDING_POST , '/singleSignOnPost'),
    ('SingleLogoutService', lasso.SAML2_METADATA_BINDING_REDIRECT , '/singleLogout', '/singleLogoutReturn'),
    ('SingleLogoutService', lasso.SAML2_METADATA_BINDING_SOAP , '/singleLogoutSOAP'),
    ('ManageNameIDService', lasso.SAML2_METADATA_BINDING_SOAP , '/manageNameIdSOAP'),
    ('ManageNameIDService', lasso.SAML2_METADATA_BINDING_REDIRECT , '/manageNameId', '/manageNameIdReturn'),
)
metadata_options = { 'key': settings.SAML_SIGNING_KEY }

def get_provider_id_and_options(provider_id):
    if not provider_id:
        provider_id=reverse(metadata)
    options = metadata_options
    if getattr(settings, 'AUTHSAML2_METADATA_OPTIONS', None):
        options.update(settings.AUTHSAML2_METADATA_OPTIONS)
    return provider_id, options

def get_metadata(request, provider_id=None):
    provider_id, options = get_provider_id_and_options(provider_id)
    return get_saml2_metadata(request, provider_id, sp_map=metadata_map,
            options=options)

def create_server(request, provider_id=None):
    provider_id, options = get_provider_id_and_options(provider_id)
    return create_saml2_server(request, provider_id, sp_map=metadata_map,
            options=options)

def http_response_bad_request(message):
    logger.error(message)
    return HttpResponseBadRequest(_(message))

def http_response_forbidden_request(message):
    logger.error(message)
    return HttpResponseForbidden(_(message))

def check_response_id(login):
    try:
        session_ext = ExtendDjangoSession.objects.get(saml_request_id=login.response.inResponseTo)
    except ExtendDjangoSession.DoesNotExist:
        return False
    return True

def build_service_provider(request):
    sp = create_server(request, reverse(metadata))
    if not sp:
        return None
    providers_list = get_idp_list()
    if not providers_list:
        return None
    for p in providers_list:
        p = load_provider(request, p.entity_id, server=sp, sp_or_idp='idp')
        if not p:
            logger.error('Unable to load provider %s' % p.entity_id)
    return sp
