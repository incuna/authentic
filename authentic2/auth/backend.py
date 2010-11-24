import urllib

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.utils.translation import gettext_noop
from django.http import HttpResponseRedirect
import django.forms

import authentic2.auth.models as models


class LoginPasswordBackend(object):
    def enabled(self):
        return True

    def name(self):
        return gettext_noop('Password')

    def id(self):
        return 'password'

    def form(self):
        return AuthenticationForm

    def post(self, request, form, nonce, next):
        # Login the user
        login(request, form.get_user())
        # Keep a trace
        if 'HTTPS' in request.environ.get('HTTPS','').lower() == 'on':
            how = 'password-on-https'
        else:
            how = 'password'
        if nonce:
            models.AuthenticationEvent(who=form.get_user().username, how=how,
                    nonce=nonce).save()
        return HttpResponseRedirect(next)

    def template(self):
        return 'auth/login_form.html'

class SSLFrontend(object):
    def enabled(self):
        return True

    def id(self):
        return 'ssl'

    def name(self):
        return gettext_noop('SSL with certificates')

    def form(self):
        return django.forms.Form

    def post(self, request, form, nonce, next):
        return HttpResponseRedirect('/sslauth?next=%s' % urllib.quote(next))

    def template(self):
        return 'auth/login_form_ssl.html'
