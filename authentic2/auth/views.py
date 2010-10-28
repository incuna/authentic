from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django import forms
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.http import urlencode
from django.contrib.sites.models import Site, RequestSite
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from authentic2.saml.common import *
import logging
import models

class WithNonceAuthenticationForm(AuthenticationForm):
    nonce = forms.CharField(label='Nonce', widget=forms.HiddenInput,
            required = False)

    def __init__(self, request = None, **kwargs):
        AuthenticationForm.__init__(self, request, **kwargs)
        if request and request.REQUEST.has_key('nonce'):
            self.initial['nonce'] = request.REQUEST.get('nonce')

    def clean(self):
        res = AuthenticationForm.clean(self)
        # create an authentication event
        if self.user_cache and self.cleaned_data.has_key('nonce'):
            how = 'password'
            if self.request and self.request.environ.has_key('HTTPS'):
                how = 'password-on-https'
            models.AuthenticationEvent(who = self.user_cache.username,
                    how = how, nonce = self.cleaned_data['nonce']).save()
        return res

@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=WithNonceAuthenticationForm):
    """Displays the login form and handles the login action."""

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- redirects to http://example.com should 
            # not be allowed, but things like /view/?param=http://example.com 
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)

    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)

    methods = []
    if settings.AUTH_SSL and request.environ.has_key('HTTPS'):
        methods.append({ 'url': '%s?%s' % (reverse('user_signin_ssl'), urlencode(request.GET)),
                         'caption': 'Login with SSL' })
        logging.info('Activation of authentication with SSL')
    if settings.AUTH_SSL and not request.environ.has_key('HTTPS'):
        logging.error('Authentication with SSL is not activated because the server is not running over HTTPS')

    if settings.AUTH_OPENID:
        methods.append({ 'url': '%s?%s' % (reverse('user_signin'), urlencode(request.GET)),
                         'caption': 'Login with OpenID' })
        logging.info('Activation of authentication with OpenID')

    return render_to_response(template_name, {
        'form': form,
        'alt_methods': methods,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'providers_list' : get_idp_list(),
    }, context_instance=RequestContext(request))


@csrf_protect
@login_required
def password_change(request, template = 'authopenid/password_change_form.html',
        post_change_redirect = None, password_change_form  = PasswordChangeForm):
    if post_change_redirect is None:
        post_change_redirect = reverse('django.contrib.auth.views.password_change_done')
    if request.method == 'POST':
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)

    if request.user.password == '!':
        context = RequestContext(request)
        context['set_password'] = True 
    else:
        context = RequestContext(request)

    return render_to_response(template, {
        'form': form,
    }, context_instance=context)

