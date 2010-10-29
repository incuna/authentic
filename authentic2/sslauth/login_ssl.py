from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext as _
from django.contrib.auth import REDIRECT_FIELD_NAME

from authentic2.saml.common import error_page
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages

# Use of existing application sslauth
from util import SSLInfo, settings_get

import logging

def process_request(request):

    ssl_info  = SSLInfo(request)

    # Check certificate validity
    if not ssl_info.verify:
        logging.error('SSL Client Authentication failed: SSL CGI variable VERIFY is missing')
        messages.add_message(request, messages.INFO, 'SSL Client Authentication failed.')
        return redirect_to_login('/')

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
            logging.error('SSL Client Authentication failed: User unknown for the current SSL context')
            messages.add_message(request, messages.INFO, 'SSL Client Authentication failed.')
            return redirect_to_login('/')

    # Check if the user is activated
    if not user.is_authenticated() or not user.is_active:
        logging.error('SSL Client Authentication failed: User %s is inactive' %user.username)
        messages.add_message(request, messages.INFO, 'SSL Client Authentication failed.')
        return redirect_to_login('/')

    # Log user in
    try:
        login(request, user)
    except:
        logging.error('SSL Client Authentication failed: login() failed')
        messages.add_message(request, messages.INFO, 'SSL Client Authentication failed.')
        return redirect_to_login('/')

    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    if redirect_to:
        logging.info('Successful SSL Client Authentication - redirection to %s' %redirect_to)
        return HttpResponseRedirect(redirect_to)

    logging.info('Successful SSL Client Authentication - redirection to /')
    return HttpResponseRedirect("/")
