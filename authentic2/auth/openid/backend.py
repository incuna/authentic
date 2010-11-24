
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django_authopenid.forms import OpenidSigninForm
from django_authopenid.utils import *
from django.core.urlresolvers import reverse

import authentic2.auth.models as models
from authentic2.auth import NONCE_FIELD_NAME
from views import ask_openid, signin_failure

class OpenIDFrontend(object):
    def enabled(self):
        return True

    def name(self):
        return 'OpenID'

    def form(self):
        return OpenidSigninForm

    def post(self, request, form, nonce, next):
        redirect_url = "%s%s?%s" % (
                get_url_host(request),
                reverse('user_complete_signin'), 
                urllib.urlencode({ REDIRECT_FIELD_NAME: next,
                    NONCE_FIELD_NAME: nonce })
        )
        return ask_openid(request,
                form.cleaned_data['openid_url'],
                redirect_url,
                on_failure=signin_failure)

    def template(self):
        return 'auth/login_form_openid.html'
