import sys
import datetime
import logging
import urllib
import lasso
from django.contrib.auth.views import redirect_to_login
from django.conf.urls.defaults import *
from django.http import *
from django.utils.translation import ugettext as _
from models import *
from authentic.saml.common import *

def fill_assertion(request, saml_request, assertion, provider_id):
    '''Stuff an assertion with information extracted from the user record
       and from the session, and eventually from transactions linked to the
       request, i.e. a login event or a consent event.'''
    # Use assertion ID as session index
    assertion.authenticationStatement.sessionIndex = assertion.assertionId
    # TODO: add attributes from user account
    # TODO: determine and add attributes from the session, for anonymous
    # users (pseudonymous federation, openid without accoutns)
    # TODO: add information from the login event, of the session or linked
    # to the request id
    # TODO: use information from the consent event to specialize release of
    # attributes (user only authorized to give its email for email)

def build_assertion(request, login):
    '''After a succesfully validated authentication request, build an
       authentication assertion'''
    now = datetime.datetime.utcnow()
    # 1 minute ago
    notBefore = now-datetime.timedelta(0,60)
    # 1 minute in the future
    notOnOrAfter = now+datetime.timedelta(0,60)
    # TODO: find authn method from login event or from session
    login.buildAssertion(lasso.LIB_AUTHN_CONTEXT_CLASS_REF_PREVIOUS_SESSION,
            now.isoformat()+'Z',
            'unused', # reauthenticateOnOrAfter is only for ID-FF 1.2
            notBefore.isoformat()+'Z',
            notOnOrAfter.isoformat()+'Z')
    assertion = login.assertion
    fill_assertion(request, login.request, assertion, login.remoteProviderId)

def metadata(request):
    '''Return ID-FFv1.2 metadata for our IdP'''
    return HttpResponse(get_idff12_metadata(request), mimetype = 'text/xml')

def consent(request, id = None, next = id, provider_id = id):
   '''On a GET produce a form asking for consentment,

       On a POST handle the form and redirect to next'''
   # TODO: implement me
   raise NotImplementedError('Implement consent')

def load_federation(request, login):
    '''Load an identity dump from the database'''
    q = LibertyIdentityDump.objects.filter(user = request.user)
    if not q:
        return
    login.setIdentityFromDump(q[0].identity_dump)

def load_session(request, login, session_key = None):
    '''Load a session dump from the database'''
    if not session_key:
        session_key = request.session.session_key
    q = LibertySessionDump.objects.filter(django_session_key = session_key)
    if not q:
        return
    login.setSessionFromDump(q[0].session_dump)

def save_federation(request, login):
    '''Save identity dump to database'''
    if login.isIdentityDirty:
        q = LibertyIdentityDump.objects.filter(user = request.user)
        if q:
            if login.identity:
                q[0].identity_dump = login.identity.dump()
            else:
                q[0].identity_dump = None
            q[0].save()
        elif login.identity:
            LibertyIdentityDump(user = request.user,
                    identity_dump = login.identity.dump()).save()

def save_session(request, login, session_key = None):
    '''Save session dump to database'''
    if not session_key:
        session_key = request.session.session_key
    if login.isSessionDirty:
        q = LibertySessionDump.objects.filter(
                django_session_key = session_key)
        if q:
            if login.session:
                q[0].session_dump = login.session.dump()
            else:
                q[0].session_dump = None
            q[0].save()
        elif login.session:
            LibertySessionDump(django_session_key = request.session.session_key,
                    session_dump = login.session.dump()).save()

# TODO: handle autoloading of metadatas
def load_provider(request, login, provider_id):
    liberty_provider = LibertyProvider.objects.get(entity_id = provider_id)
    if not liberty_provider:
        return False
    login.server.addProviderFromBuffer(lasso.PROVIDER_ROLE_SP,
            liberty_provider.metadata.read())
    return True

def save_artifact(request, login):
    LibertyArtifact(artifact = login.assertionArtifact,
            django_session_key = request.session.session_key,
            provider_id = login.remoteProviderId).save()

# TODO: handle cancellation, by retrieving a login event and looking for
# cancelled flag
# TODO: handle force_authn by redirecting to the login page with a parameter
# linking the login event with this request id and next=current_path
def sso(request):
    """Endpoint for AuthnRequests asynchronously sent, i.e. POST or Redirect"""
    # 1. Process the request, separate POST and GET treatment
    message = get_idff12_request_message(request)
    if not message:
        return HttpResponseForbidden('Invalid SAML 1.1 AuthnRequest: "%s"' % message)
    server = create_idff12_server(request)
    login = lasso.Login(server)
    while True:
        try:
            login.processAuthnRequestMsg(message)
            break
        except lasso.DsInvalidSignatureError:
            message = _('Invalid signature on SAML 1.1 AuthnRequest: %r') % message
            logging.error(message)
            return HttpResponseForbidden()
        except lasso.ProfileInvalidMsgError:
            message = _('Invalid SAML 1.1 AuthnRequest: %r') % message
            logging.error(message)
            return HttpResponseForbidden()
        except lasso.ServerProviderNotFoundError:
            # This path is not exceptionnal it should be normal since we did
            # not load any provider in the Server object
            provider_id = login.remoteProviderId
            # 2. Lookup the ProviderID
            logging.info(_('ID-FFv1.2: AuthnRequest from %r')
                    % provider_id)
            provider_loaded = load_provider(request, login, provider_id)
            if not provider_loaded:
                consent_obtained = False
                message = _('ID-FFv1.2: provider %r unknown') % provider_id
                logging.warning(message)
                return HttpResponseForbidden(message)
            else:
                # XXX: does consent be always automatic for known providers ? Maybe
                # add a configuration key on the provider.
                consent_obtained = True
    # Flags possible:
    # - consent
    # - isPassive
    # - forceAuthn
    #
    # 3. TODO: Check for permission
    if login.mustAuthenticate():
        # TODO:
        # check that it exists a login transaction for this request id
        #  - if there is, then provoke one with a redirect to
        #  login?next=<current_url>
        #  - if there is then set user_authenticated to the result of the
        #  login event
        # Work around lack of informations returned by mustAuthenticate()
        if login.request.forceAuthn or request.user.is_anonymous():
            return redirect_to_login(request.build_absolute_uri())
        else:
            user_authenticated = True
    else:
        user_authenticated = not request.user.is_anonymous()
    # 3.1 Ask for consent
    if user_authenticated:
        # TODO: for autoloaded providers always ask for consent
        if login.mustAskForConsent() or not consent_obtained:
            # TODO: replace False by check against request id
            if False:
                consent_obtained = True
            # i.e. redirect to /idp/consent?id=requestId
            # then check that Consent(id=requestId) exists in the database
            else:
                return HttpResponseRedirect('consent?id=%s&next=%s' %
                        ( login.request.requestId,
                            urllib.quote(request.build_absolute_uri())) )
    # 4. Validate the request, passing authentication and consent status
    try:
        login.validateRequestMsg(user_authenticated, consent_obtained)
    except:
        raise
        do_federation = False
    else:
        do_federation = True
    # 5. Lookup the federations
    if do_federation:
        load_federation(request, login)
        load_session(request, login)
        # 3. Build and assertion, fill attributes
        build_assertion(request, login)
    # 4. build response
    if login.protocolProfile == lasso.LOGIN_PROTOCOL_PROFILE_BRWS_ART:
        login.buildArtifactMsg(lasso.HTTP_METHOD_REDIRECT)
        save_artifact(request, login)
    elif login.protocolProfile == lasso.LOGIN_PROTOCOL_PROFILE_BRWS_POST:
        login.buildAuthnResponseMsg()
    else:
        raise NotImplementedError()
    save_federation(request, login)
    save_session(request, login)
    return return_idff12_response(login, title = _('Authentication response'))

def artifact_resolve(request, soap_message):
    pass

def soap(request):
    '''SAMLv1.1 soap endpoint implementation.

       It should handle request for:
        - artifact resolution
        - logout
        - and federation termination'''
    soap_message = get_soap_message(request)
    request_type = lasso.getRequestTypeFromSoapMsg(soap_message)
    if request_type == lasso.REQUEST_TYPE_LOGIN:
        return artifact_resolve(request, soap_message)
    else:
        message = _('ID-FFv1.2: soap request type %r is currently not supported') % request_type
        logging.warning(message)
        return NotImplementedError(message)

def finish_sso(request, login):
    pass

def finish_failed_sso(request, login):
    pass

urlpatterns = patterns('',
    (r'^metadata$', metadata),
    (r'^sso$', sso),
    (r'^soap$', soap),
)
