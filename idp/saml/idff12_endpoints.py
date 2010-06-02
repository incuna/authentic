from django.contrib.auth.decorators import login_required
from django.conf.urls.defaults import *
from django.http import *
import lasso
from models import *
from authentic.saml.common import *
import datetime

def metadata(request):
    return HttpResponse(get_idff12_metadata(request), mimetype = 'text/xml')

@login_required
def sso(request):
    """Endpoint for AuthnRequests asynchronously sent, i.e. POST or Redirect"""
    # 1. Process the request, separate POST and GET treatment
    message = get_idff12_request_message(request)
    if not message:
        return HttpResponseForbidden('Invalid SAML 1.1 AuthnRequest: "%s"' % message)
    server = create_idff12_server(request)
    login = lasso.Login(server)
    try:
        login.processAuthnRequestMsg(message)
    except lasso.ProfileInvalidMsgError:
        return HttpResponseForbidden('Invalid SAML 1.1 AuthnRequest: "%s"' % message)

    # 2. Lookup the ProviderID

    # 3. Check for permission

    # 3. Build and assertion, fill attributes

    # 3. Depending on the requested profile finish with an artifact or a
    # POST

urlpatterns = patterns('',
    (r'^metadata/', metadata),
    (r'^sso/', sso),
)
