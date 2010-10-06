from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import *

NONCE = 'nonce'

def redirect_to_login(next, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME, other_keys = {}):
    "Redirects the user to the login page, passing the given 'next' page"
    if not login_url:
        login_url = settings.LOGIN_URL
    data = { urlquote(redirect_field_name): urlquote(login_url) }
    for k, v in other_keys.iteritems():
        data[urlquote(k)] = urlquote(v)
    return HttpResponseRedirect('%s?%s' % urlencode(data))

def save_login_object(login, consent_obtained, nonce):
    raise NotImplementedError()

def load_login_object(nonce):
    raise NotImplementedError()

def get_nonce_dict(cookie):
    # TODO: implement me
    return False
