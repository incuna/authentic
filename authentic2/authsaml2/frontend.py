import urllib
import functools
import django.forms as forms
import authentic2.saml.common as saml_common

from django.utils.translation import gettext_noop
from django.http import HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME

from authentic2.authsaml2.saml2_endpoints import view_profile

class AuthSAML2Form(forms.Form):
    def __init__(self, *args, **kwargs):
        idp_list = kwargs.pop('idp_list')
        super(AuthSAML2Form, self).__init__(*args, **kwargs)
        self.fields['provider_id'].choices = \
                [(p['entity_id'], p['name']) for p in idp_list]

    provider_id = forms.ChoiceField(label='Choose your identity provider',
            choices=())

class AuthSAML2Frontend(object):
    def __init__(self):
        self.idp_list = saml_common.get_idp_list_sorted()

    def enabled(self):
        return bool(self.idp_list)

    def id(self):
        return 'saml2'

    def name(self):
        return gettext_noop('SAML 2.0')

    def form(self):
        return functools.partial(AuthSAML2Form, idp_list=self.idp_list)

    def post(self, request, form, nonce, next):
        provider_id = form.cleaned_data['provider_id']
        return HttpResponseRedirect('/authsaml2/sso?entity_id=%s&%s=%s' %
                (urllib.quote(provider_id),
                REDIRECT_FIELD_NAME,
                urllib.quote(next)))

    def get_context(self):
        '''Specific context variable used by the specific template'''
        return { 'idp_providers': self.idp_list }

    def template(self):
        return 'auth/saml2/login_form.html'

    def profile(self, request, next=''):
        return view_profile(request, next)
