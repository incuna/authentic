from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from util import SSLInfo, settings_get
from django.contrib.auth.middleware import AuthenticationMiddleware

from middleware import SSLAuthMiddleware

def process_request(request):

    ssl_info  = SSLInfo(request)
    if ssl_info.__dict__['verify']:
        user = authenticate(ssl_info=ssl_info) or AnonymousUser()
        if not user.is_authenticated() and ssl_info.verify and settings_get('SSLAUTH_CREATE_USER'):
            from backends import SSLAuthBackend
            if SSLAuthBackend().create_user(ssl_info):
                user = authenticate(ssl_info=ssl_info) or AnonymousUser()

        login(request, user)
        return HttpResponseRedirect("/")

    else:
        html = "<html><body>SSL Login Error.</body></html>"
        return HttpResponse(html)


