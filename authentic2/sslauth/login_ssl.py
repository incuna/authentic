from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import AnonymousUser

from authentic2.saml.common import error_page

# Use of existing application sslauth
from util import SSLInfo, settings_get

def process_request(request):

    ssl_info  = SSLInfo(request)

    # Check certificate validity
    if not ssl_info.verify:
        return error_page('SSL CGI variable VERIFY is missing')

    # Kill another active session
    logout(request)

    # return a known user else an anonymous one
    user = authenticate(ssl_info=ssl_info) or AnonymousUser()

    # Add user entry if unknown
    # TODO: With Admin set SSLAUTH_CREATE_USER
    # then define in SSLAUTH_CREATE_USERNAME_CALLBACK = myusernamegen
    # and modify myusernamegen:
    # def myusernamegen(ssl_info):
    #    import re
    #    if(ssl_info.subject_cn):
    #        return return re.sub('[^a-zA-Z0-9]', '_', ssl_info.subject_cn)
    #    else:
    #        return return re.sub('[^a-zA-Z0-9]', '_', ssl_info.serial)
    # TODO: With admin associate a certificate with a user
    # else unusable without SSLAUTH_CREATE_USER
    # SSLAUTH_STRICT_MATCH to match a user with all the certificate content which matches
    # if SSLAUTH_SUBJECT_MATCH_KEYS
    # else 'subject_email', 'subject_cn', 'subject_o'
    if not user.is_authenticated():
        if settings_get('SSLAUTH_CREATE_USER'):
            from backends import SSLAuthBackend
            if SSLAuthBackend().create_user(ssl_info):
                user = authenticate(ssl_info=ssl_info)
        else:
            return error_page('User unknown for the current SSL context')

    # Check if the user is activated
    if not user.is_authenticated() or not user.is_active:
        return error_page('User %s is inactive' % user.username)

    # Log user in
    login(request, user)
    return HttpResponseRedirect("/")
