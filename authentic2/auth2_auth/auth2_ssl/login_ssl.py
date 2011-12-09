import logging
import urllib

import django.forms
import authentic2.auth2_auth.models as auth_models
import views


from django.conf import settings
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth import REDIRECT_FIELD_NAME

from authentic2.auth2_auth import NONCE_FIELD_NAME
from authentic2.saml.common import error_page

from models import ClientCertificate, DistinguishedName
from util import SSLInfo, settings_get

logger = logging.getLogger('authentic2.auth2_auth.auth2_ssl')

def handle_request(request,):
    next = request.REQUEST.get(REDIRECT_FIELD_NAME)
    if not next:
        if 'next' in request.session:
            next = request.session['next']
        elif settings.LOGIN_REDIRECT_URL:
            next = settings.LOGIN_REDIRECT_URL
        else:
            next = '/'

    # Check certificate validity
    ssl_info  = SSLInfo(request)
    accept_self_signed = \
        getattr(settings, 'SSLAUTH_ACCEPT_SELF_SIGNED', False)

    if not ssl_info.cert:
        logger.error('auth2_ssl: SSL Client Authentication failed: \
            SSL CGI variable CERT is missing')
        messages.add_message(request, messages.ERROR,
            _('SSL Client Authentication failed. \
            No client certificate found.'))
        return redirect_to_login(next)
    elif not accept_self_signed and not ssl_info.verify:
        logger.error('auth2_ssl: SSL Client Authentication failed: \
            SSL CGI variable VERIFY is not SUCCESS')
        messages.add_message(request, messages.ERROR,
            _('SSL Client Authentication failed. \
            Your client certificate is not valid.'))
        return redirect_to_login(next)

    # SSL entries for this certificate?
    user = authenticate(ssl_info=ssl_info)

    # If the user is logged in, no need to create an account
    # If there is an SSL entries, no need for account creation,
    # just need to login, treated after
    if 'do_creation' in request.session and not user \
            and not request.user.is_authenticated():
        from backend import SSLBackend
        logger.info('auth2_ssl: Account creation treatment')
        if SSLBackend().create_user(ssl_info):
            user = authenticate(ssl_info=ssl_info)
            logger.info('auth2_ssl: account created for %s' % user.username)
        else:
            logger.error('auth2_ssl: account creation failure')
            messages.add_message(request, messages.ERROR,
            _('SSL Client Authentication failed. Internal server error.'))
            return HttpResponseRedirect(next)

    # No SSL entries and no user session, redirect account linking page
    if not user and not request.user.is_authenticated():
        return render_to_response('auth/account_linking_ssl.html',
                context_instance=RequestContext(request))

    # No SSL entries but active user session, perform account linking
    if not user and request.user.is_authenticated():
        from backend import SSLBackend
        if SSLBackend().link_user(ssl_info, request.user):
            logger.info('auth2_ssl: Successful linking of the SSL \
               Certificate to an account, redirection to %s' % next)
        else:
            logger.error('auth2_ssl: login() failed')
            messages.add_message(request, messages.ERROR,
            _('SSL Client Authentication failed. Internal server error.'))
        return HttpResponseRedirect(next)

    # SSL Entries found for this certificate,
    # if the user is logged out, we login
    if not request.user.is_authenticated():
        try:
            login(request, user)
            auth_models.AuthenticationEvent.objects.create(who=user.username,
                    how='ssl', nonce=request.GET.get(NONCE_FIELD_NAME,''))
        except:
            logger.error('auth2_ssl: login() failed')
            messages.add_message(request, messages.ERROR,
                _('SSL Client Authentication failed. Internal server error.'))
            return redirect_to_login(next)

        logger.info('auth2_ssl: Successful SSL Client Authentication, \
            redirection to %s' % next)
        return HttpResponseRedirect(next)

    # SSL Entries found for this certificate, if the user is logged in, we
    # check that the SSL entry for the certificate is this user.
    # else, we make this certificate point on that user.
    if user.username != request.user.username:
        logger.warning('[auth2_ssl]: The certificate belongs to %s, \
            but %s is logged with, we change the association!' \
            %(user.username, request.user.username))
        from backend import SSLBackend
        cert = SSLBackend().get_certificate(ssl_info)
        cert.user = request.user
        cert.save()

    logger.info('auth2_ssl: Successful SSL Client Authentication, \
        redirection to %s' % next)
    return HttpResponseRedirect(next)

###
 # post_account_linking
 # @request
 #
 # Called after an account linking.
 ###
@csrf_exempt
def post_account_linking(request):
    logger.info('auth2_ssl Return after account linking form filled')
    if request.method == "POST":
        if 'do_creation' in request.POST \
                and request.POST['do_creation'] == 'on':
            logger.info('auth2_ssl: account creation asked')
            request.session['do_creation'] = 'do_creation'
            if 'next' in request.session:
                next = request.session['next']
            else:
                next = request.path
            qs = { REDIRECT_FIELD_NAME: next }
            return HttpResponseRedirect('/sslauth?%s' % urllib.urlencode(qs))
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            logger.info('auth2_ssl: form valid')
            user = form.get_user()
            try:
                login(request, user)
                auth_models.AuthenticationEvent.objects.create(who=user.username,
                how='password', nonce=request.GET.get(NONCE_FIELD_NAME,''))
            except:
                logger.error('auth2_ssl: login() failed')
                messages.add_message(request, messages.ERROR,
                _('SSL Client Authentication failed. Internal server error.'))

            logger.debug('auth2_ssl: session opened')

            #if request.session.has_key('next'):
            #    next = request.session['next']
            #else:
            #    next = request.path
            #logger.debug('auth2_ssl: next %s' %next)
            #qs = { REDIRECT_FIELD_NAME: next }
            #if nonce is not None:
            #    qs.update({ NONCE_FIELD_NAME: nonce })
            #return HttpResponseRedirect('/sslauth?%s' % urllib.urlencode(qs))
            return HttpResponseRedirect('/sslauth')
        else:
            logger.warning('auth2_ssl: \
                form not valid - Try again! (Brute force?)')
            return render_to_response('auth/account_linking_ssl.html',
                    context_instance=RequestContext(request))
    else:
        return render_to_response('auth/account_linking_ssl.html',
                context_instance=RequestContext(request))

def profile(request, next='', template_name='ssl/profile.html'):
    if 'next' in request.session:
        next = request.session['next']
    else:
        next = next
    if request.user is None \
        or not request.user.is_authenticated() \
        or not hasattr(request.user, '_meta'):
        return HttpResponseRedirect(next)

    certificates = []
    try:
        certs = ClientCertificate.objects.filter(user=request.user)
        for c in certs:
            vals = [ "%s=%s" \
                % (key, c.subject.__getattribute__(key.lower())) \
                for key in ( 'CN', 'OU', 'O', 'C', 'Email' ) \
                if c.subject.__getattribute__(key.lower()) ]
            certificates.append("/".join(vals))
    except:
        pass

    return render_to_string(template_name,
            { 'certificates': certificates,
              'next': next,
              'base': '/ssl'},
            RequestContext(request))

def delete_certificate(request, next='/'):
    if 'next' in request.session:
        next = request.session['next']
    else:
        next = next
    if request.user is None \
        or not request.user.is_authenticated() \
        or not hasattr(request.user, '_meta'):
        return HttpResponseRedirect(next)

    if not 'cert_name' in request.POST:
        logger.error('auth2_ssl: No certificate name provided for deletion')
        messages.add_message(request, messages.ERROR,
            _('No certificate name provided for deletion.'))
        return HttpResponseRedirect(next)

    certificates = []
    try:
        certs = ClientCertificate.objects.filter(user=request.user)
        for c in certs:
            vals = [ "%s=%s" \
                % (key, c.subject.__getattribute__(key.lower())) \
                for key in ( 'CN', 'OU', 'O', 'C', 'Email' ) \
                if c.subject.__getattribute__(key.lower()) ]
            s = "/".join(vals)
            logger.debug('auth2_ssl: certificate %s found ' %s)
            if request.POST['cert_name'] == s:
                logger.info('auth2_ssl: Deletion of certificate %s found ' \
                    %s)
                messages.add_message(request, messages.INFO,
                _('Successful certificate deletion.'))
                c.delete()
                return HttpResponseRedirect('/profile')
    except:
        pass

    logger.error('auth2_ssl: asked deletion of certificate not found %s ' \
        %request.POST['cert_name'])
    messages.add_message(request, messages.ERROR,
        _('Certificate deletion failed.'))
    return HttpResponseRedirect(next)
