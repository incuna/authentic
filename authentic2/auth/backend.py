
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.http import HttpResponseRedirect

import authentic2.auth.models as models


class LoginPasswordBackend(object):
    def name(self):
        return 'Password'

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
