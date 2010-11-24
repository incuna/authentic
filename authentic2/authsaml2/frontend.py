from django.utils.translation import gettext_noop
import django.forms as forms
from django.http import HttpResponseRedirect

import authentic2.saml.common as saml_common

class AuthSAML2Form(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AuthSAML2Form, self).__init__(*args, **kwargs)
        self.fields['provider_id'].choices = \
                [(p.entity_id, p.name) for p in saml_common.get_idp_list()]

    provider_id = forms.ChoiceField(label='Choose your identity provider',
            choices=())

class AuthSAML2Frontend(object):
    def enabled(self):
        return bool(saml_common.get_idp_list())

    def id(self):
        return 'saml2'

    def name(self):
        return gettext_noop('SAML 2.0')

    def form(self):
        return AuthSAML2Form

    def post(self, request, form, nonce, next):
        provider_id = form.cleaned_data['provider_id']
        return HttpResponseRedirect('/authsaml2/selectProvider/%s' %
                urllib.quote(provider_id))

    def template(self):
        return 'auth/login_form_ssl.html'
