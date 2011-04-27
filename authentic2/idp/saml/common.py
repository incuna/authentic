import logging

from django.contrib.auth import REDIRECT_FIELD_NAME, SESSION_KEY
from django.utils.http import urlencode
from django.utils.importlib import import_module
from django.conf import settings
from django.http import HttpResponseRedirect

def redirect_to_login(next, login_url=None,
        redirect_field_name=REDIRECT_FIELD_NAME, other_keys = {}):
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

def kill_django_sessions(session_key):
    engine = import_module(settings.SESSION_ENGINE)
    try:
        for key in session_key:
            store = engine.SessionStore(key)
            logging.debug('Killing session %s of user %s' %
                    (key, store[SESSION_KEY]))
            store.delete()
    except Exception, e:
        logging.error(e)
