import datetime
import lasso
import logging

from authentic.saml.common import *
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.http import *
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from authentic.saml.models import *
from common import redirect_to_login
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required

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

def metadata(request):
    return HttpResponse(get_saml2_metadata(request), mimetype = 'text/xml')


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
    server = create_saml2_server(request)
    login = lasso.Login(server)
    # 1. Process the request, separate POST and GET treatment
    message = get_idff12_request_message(request)
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
        except lasso.ProfileInvalidProtocolProfileError:
            log_info_authn_request_details(login)
            message = N_('SAMLv2: sso request cannot be answered because no valid protocol binding could be found')
            logging.error(message)
            return HttpResponseBadRequest(_(message))
        except lasso.DsError:
            log_info_authn_request_details(login)
            logging.error('SAMLv2: sso request signature validation failed: %s' % e)
            return finish_sso(request, login)
        except (lasso.ServerProviderNotFoundError, lasso.ProfileUnkownProviderError):
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
    return sso_after_process_request(request, login,
        consent_obtained = consent_obtained)

def need_login(request, login, consent_obtained):
    '''Redirect to the login page with a nonce parameter to verify later that the login form was submitted'''
    nonce = login.request.id
    save_login_object(login, consent_obtained, nonce)
    return redirect_to_login(request.get_full_path(),
            other_keys = { NONCE : nonce })

def need_consent(request, login, consent_obtained):
    nonce = login.request.id
    save_login_object(login, consent_obtained, nonce)
    return HttpResponseRedirect('%s?id=%s&next=%s' %
            ( reverse(consent), nonce,
                urllib.quote(request.get_full_path())) )

def continue_sso(request):
    nonce = request.REQUEST.get(NONCE, '')
    login, consent_obtained, save = load_login_object(nonce)
    if not login:
        logging.debug('SAMLv2: continue sso nonce %r not found' % nonce)
        return HttpResponseBadRequest()
    return sso_after_process_request(request, login,
            consent_obtained = consent_obtained, save = True)

def sso_after_process_request(request, login,
        consent_obtained = True, user = None, save = True):
    '''Common path for sso and idp_initiated_sso.

       consent_obtained: whether the user has given his consent to this federation
       user: the user which must be federated, if None, current user is the default.
       save: whether to save the result of this transaction or not.
    '''
    nonce = login.request.id
    nonce_dict = get_nonce_dict(nonce)
    if not nonce_dict.has_key('cancelled'):
        if user is None:
            user = request.user
        # Flags possible:
        # - consent
        # - isPassive
        # - forceAuthn
        #
        # 3. TODO: Check for permission
        if request.user.anonymous:
            return need_login(request, login)
        if login.mustAuthenticate():
            # TODO:
            # check that it exists a login transaction for this request id
            #  - if there is, then provoke one with a redirect to
            #  login?next=<current_url>
            #  - if there is then set user_authenticated to the result of the
            #  login event
            # Work around lack of informations returned by mustAuthenticate()
            if login.request.forceAuthn and not nonce_dict.get('authentified','') == request.user:
                return need_login(request, login)
        # TODO: for autoloaded providers always ask for consent
        if login.mustAskForConsent() or not consent_obtained:
            # TODO: replace False by check against request id
            if nonce_dict.has_key('consent'):
                consent_obtained = True
            elif nonce_dict.has_key('forbid'):
                consent_obtained = False
            # i.e. redirect to /idp/consent?id=requestId
            # then check that Consent(id=requestId) exists in the database
            else:
                return need_consent(request, login, consent_obtained)
    # 4. Validate the request, passing authentication and consent status
    try:
        login.validateRequestMsg(user_authenticated, consent_obtained)
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
        build_assertion(request, login)
    return finish_sso(request, login, user = user, save = save)


urlpatterns = patterns('',
    (r'^metadata$', metadata),
    (r'^sso', sso),
)

