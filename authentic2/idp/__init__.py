import logging

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def load_backend(path):
    '''Load an IdP backend by its module path'''
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing idp backend %s: "%s"' % (module, e))
    except ValueError, e:
        raise ImproperlyConfigured('Error importing idp backends. Is IDP_BACKENDS a correctly defined list or tuple?')
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" idp backend' % (module, attr))
    return cls()

def get_backends(setting_name='IDP_BACKENDS'):
    '''Return the list of IdP backends'''
    backends = []
    for backend_path in getattr(settings, setting_name, ()):
        backends.append(load_backend(backend_path))
    return backends
