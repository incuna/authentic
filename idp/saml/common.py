from django.shortcuts import render_to_response
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import *
from django.utils.html import escape
from django.conf import settings
from django.http import *

NONCE = 'nonce'

def redirect_to_login(next, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME, other_keys = {}):
    "Redirects the user to the login page, passing the given 'next' page"
    if not login_url:
        login_url = settings.LOGIN_URL
    data = { redirect_field_name: next }
    for k, v in other_keys.iteritems():
        data[k] = v
    return HttpResponseRedirect('%s?%s' % (login_url, urlencode(data)))

def save_login_object(login, consent_obtained, nonce):
    raise NotImplementedError()

def load_login_object(nonce):
    raise NotImplementedError()
