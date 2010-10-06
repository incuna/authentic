from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import login as old_login
from django import forms
import models

class WithNonceAuthenticationForm(AuthenticationForm):
    nonce = forms.CharField(label='Nonce', widget=forms.HiddenInput)

    def __init__(self, request = None, **kwargs):
        AuthenticationForm.__init__(self, request, **kwargs)
        if request and request.REQUEST.has_key('nonce'):
            print 'setting nonce to', request.REQUEST.get('nonce')
            self.initial['nonce'] = request.REQUEST.get('nonce')
            print self

    def clean(self):
        res = AuthenticationForm.clean(self)
        # create an authentication event
        if self.cleaned_data.has_key('nonce'):
            how = 'password'
            if self.request.environ.has_key('HTTPS'):
                how = 'password-on-https'
            models.AuthenticationEvent(who = self.user_cache.username,
                    how = how, nonce = self['nonce']).save()
        return res

def login(request):
    return old_login(request,
            authentication_form=WithNonceAuthenticationForm)
