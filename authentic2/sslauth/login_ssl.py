from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import ugettext as _
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.core.urlresolvers import reverse

from authentic2.saml.common import error_page
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages

# Use of existing application sslauth
from util import SSLInfo, settings_get
import views
import authentic2.auth.models as auth_models
from authentic2.auth import NONCE_FIELD_NAME

import logging

def process_request(request,):
    next = request.GET.get(REDIRECT_FIELD_NAME,settings.LOGIN_REDIRECT_URL)
    ssl_info  = SSLInfo(request)
    # Check certificate validity
    accept_self_signed = getattr(settings, 'SSLAUTH_ACCEPT_SELF_SIGNED', False)

    if not ssl_info.cert:
        logging.error('SSL Client Authentication failed: SSL CGI variable CERT is missing')
        messages.add_message(request, messages.ERROR, _('SSL Client Authentication failed. No client certificate found.'))
        return redirect_to_login(next)
    elif not accept_self_signed and not ssl_info.verify:
        logging.error('SSL Client Authentication failed: SSL CGI variable VERIFY is not SUCCESS')
        messages.add_message(request, messages.ERROR, _('SSL Client Authentication failed. Your client certificate is not valid.'))
        return redirect_to_login(next)

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
            if accept_self_signed:
                url = '%s?next=%s' % (reverse(views.register), next)
                return HttpResponseRedirect(url)
            else:
                from backends import SSLAuthBackend
                if SSLAuthBackend().create_user(ssl_info):
                    user = authenticate(ssl_info=ssl_info)
        else:
            logging.error('SSL Client Authentication failed: User unknown for the current SSL context')
            messages.add_message(request, messages.ERROR, _('SSL Client Authentication failed. No user matches your certificate.'))
            return redirect_to_login(next)

    # Check if the user is activated
    if not user.is_authenticated() or not user.is_active:
        logging.error('SSL Client Authentication failed: User %s is inactive' %user.username)
        messages.add_message(request, messages.ERROR, 'SSL Client Authentication failed. Your user is inactive.')
        return redirect_to_login(next)

    # Log user in
    try:
        login(request, user)
        auth_models.AuthenticationEvent.objects.create(who=user.username,
                how='ssl', nonce=request.GET.get(NONCE_FIELD_NAME,''))
    except:
        logging.error('SSL Client Authentication failed: login() failed')
        messages.add_message(request, messages.ERROR, _('SSL Client Authentication failed. Internal server error.'))
        return redirect_to_login(next)

    logging.info('Successful SSL Client Authentication - redirection to %s' % next)
    return HttpResponseRedirect(next)
