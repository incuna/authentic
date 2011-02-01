import logging
import urllib

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
from django.template.loader import render_to_string

from authentic2.saml.common import *
from authentic2.auth import NONCE_FIELD_NAME
from authentic2.idp import get_backends
import models

class WithNonceAuthenticationForm(AuthenticationForm):
    nonce = forms.CharField(label='Nonce', widget=forms.HiddenInput,
            required = False)

    def __init__(self, request = None, **kwargs):
        AuthenticationForm.__init__(self, request, **kwargs)
        if request and request.REQUEST.has_key(NONCE_FIELD_NAME):
            self.initial[NONCE_FIELD_NAME] = request.REQUEST.get(NONCE_FIELD_NAME)

    def clean(self):
        res = AuthenticationForm.clean(self)
        # create an authentication event
        if self.user_cache and self.cleaned_data.has_key(NONCE_FIELD_NAME):
            how = 'password'
            if self.request and self.request.environ.has_key('HTTPS'):
                how = 'password-on-https'
            models.AuthenticationEvent(who=self.user_cache.username,
                    how=how, nonce=self.cleaned_data[NONCE_FIELD_NAME]).save()
        return res

def add_arg(url, key, value = None):
    '''Add a parameter to an URL'''
    key = urllib.quote(key)
    if value is not None:
        add = '%s=%s' % (key, urllib.quote(value))
    else:
        add = key
    if '?' in url:
        return '%s&%s' % (url, add)
    else:
        return '%s?%s' % (url, add)

@csrf_protect
@never_cache
def login(request, template_name='auth/login.html',
          login_form_template='auth/login_form.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=WithNonceAuthenticationForm):
    """Displays the login form and handles the login action."""

    redirect_to = request.REQUEST.get(redirect_field_name)
    if not redirect_to or ' ' in redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL
    # Heavier security check -- redirects to http://example.com should 
    # not be allowed, but things like /view/?param=http://example.com 
    # should be allowed. This regex checks if there is a '//' *before* a
    # question mark.
    elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
            redirect_to = settings.LOGIN_REDIRECT_URL
    nonce = request.REQUEST.get(NONCE_FIELD_NAME)

    frontends = get_backends('AUTH_FRONTENDS')

    # If already logged, leave now
    if not request.user.is_anonymous() \
            and nonce is None \
            and request.method != 'POST':
        return HttpResponseRedirect(redirect_to)

    if request.method == "POST":
        if 'cancel' in request.POST:
            redirect_to = add_arg(redirect_to, 'cancel')
            return HttpResponseRedirect(redirect_to)
        else:
            forms = []
            for frontend in frontends:
                if not frontend.enabled():
                    continue
                if 'submit-%s' % frontend.id() in request.POST:
                    form = frontend.form()(data=request.POST)
                    if form.is_valid():
                        if request.session.test_cookie_worked():
                            request.session.delete_test_cookie()
                        return frontend.post(request, form, nonce, redirect_to)
                    forms.append((frontend.name(), {'form': form, 'backend': frontend}))
                else:
                    forms.append((frontend.name(), {'form': frontend.form()(), 'backend': frontend}))
    else:
        forms = [(frontend.name(), { 'form': frontend.form()(), 'backend': frontend }) \
                for frontend in frontends if frontend.enabled()]

    rendered_forms = []
    for name, d in forms:
        context = { 'cancel': nonce is not None,
                    'submit_name': 'submit-%s' % d['backend'].id(),
                    redirect_field_name: redirect_to,
                    'form': d['form'] }
        if hasattr(d['backend'], 'get_context'):
            context.update(d['backend'].get_context())
        rendered_forms.append((name,
            render_to_string(d['backend'].template(),
                RequestContext(request, context))))

    request.session.set_test_cookie()

    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)

    return render_to_response(template_name, {
        'methods': rendered_forms,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
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

def login_password_profile(request, next):
    return render_to_string('auth/login_password_profile.html', {},
            RequestContext(request))


def redirect_to_login(request, next=None, nonce=None, keep_qs=False):
    '''Redirect to the login, eventually adding a nonce'''
    if next is None:
        if keep_qs:
            next = request.build_absolute_uri()
        else:
            next = request.build_absolute_uri(request.path)
    qs = { REDIRECT_FIELD_NAME: next }
    if nonce is not None:
        qs.update({ NONCE_FIELD_NAME: nonce })
    return HttpResponseRedirect('/login?%s' % urlencode(qs))
