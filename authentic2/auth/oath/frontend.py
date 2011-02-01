from django.utils.translation import ugettext as _
from django.utils.translation import gettext_noop
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
import django.forms as forms

import authentic2.auth.models as models
import views

# Only difference with login/password form is the user of 'otp' intead of
# password as an argument to the authenticate() method
# So you need an OTP enabled backend to this to work
class OATHOTPHAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, oath_otp=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct username and one-time password. Note that both fields are case-sensitive."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))

        return self.cleaned_data


class OATHOTPFrontend(object):
    def enabled(self):
        return True

    def name(self):
        return gettext_noop('One time password')

    def id(self):
        return 'oath-otp'

    def form(self):
        return OATHOTPHAuthenticationForm

    def post(self, request, form, nonce, next):
        # Login the user
        login(request, form.get_user())
        # Keep a trace
        if 'HTTPS' in request.environ.get('HTTPS','').lower() == 'on':
            how = 'oath-otp-on-https'
        else:
            how = 'oath-otp'
        if nonce:
            models.AuthenticationEvent(who=form.get_user_id(), how=how,
                    nonce=nonce).save()
        return HttpResponseRedirect(next)

    def profile(self, request, next=''):
        return views.totp_profile(request, next)

    def template(self):
        return 'auth/login_form_oath.html'
