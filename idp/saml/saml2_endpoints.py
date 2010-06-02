import datetime
import lasso

from authentic.saml.common import *
from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.http import *
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from models import *

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
    return HttpResponse(get_saml2_metadata(request), mimetype = 'text/xml')

@login_required
def sso(request):
    """Endpoint for receiving saml2:AuthnRequests by POST, Redirect or SOAP.
       For SOAP a session must be established previously through the login page. No authentication through the SOAP request is supported.
    """
    message = get_saml2_request_message(request)
    server = create_saml2_server(request)
    login = lasso.Login(server)
    try:
        login.processAuthnRequestMsg(message)
    except lasso.ProfileInvalidMsgError:
        return HttpResponseBadRequest('The SAML AuthnRequest is invalid: "%s"' % message)
    except lasso.ServerProviderNotFoundError:
        # Lookup the provider
        q=LibertyProvider.objects.filter(entity_id=login.remoteProviderId)
        if not q:
            # FIXME: auto load the provider
            return finish_sso(request, login)
        server.addProvider(lasso.PROVIDER_ROLE_SP, q.metadata.read())
    login.validateRequest(True, True)
    now = datetime.datetime.utcnow()
    notBefore = now-datetime.timedelta(0,60)
    notOnOrAfter = now+datetime.timedelta(0,60)
    login.buildAssertion(get_saml2_authn_method(session),
            now.isoformat()+'Z',
            'unused', # reauthenticateOnOrAfter is only for ID-FF 1.2
            notBefore.isoformat()+'Z',
            notOnOrAfter.isoformat()+'Z')
    assertion = login.response.assertion[0]
    # Use assertion ID as session index
    assertion.authnStatement[0].sessionIndex = assertion.iD
    # Save assertion with the current session
    # XXX: add support of artifact and split this function
    if login.msgBody:
        return render_to_response('saml/post_form.html',{
            'title': _("Authentication Request"),
            'url': login.msgUrl,
            'fieldname': 'SAMLResponse',
            'body': login.msgBody,
            'relay_state': login.msgRelayState })

def finish_sso(request, login):
    login.buildResponseMsg(login)
    return get_saml2_response(login)

urlpatterns = patterns('',
    (r'^metadata/', metadata),
    (r'^sso/', sso),
)

