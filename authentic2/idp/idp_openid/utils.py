# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 fdm=indent : */
# some code from http://www.djangosnippets.org/snippets/310/ by simon
# and from examples/djopenid from python-openid-2.2.4

import openid.server
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.http import HttpResponse, HttpResponseRedirect

import conf

def oresponse_to_response(server, oresponse):
    try:
        webresponse = server.encodeResponse(oresponse)
    except openid.server.EncodingError:
        return HttpResponseRedirect('/')
    response = HttpResponse(webresponse.body)
    response.status_code = webresponse.code
    for key, value in webresponse.headers.items():
        response[key] = value
    return response

def import_module_attr(path):
    package, module = path.rsplit('.', 1)
    return getattr(import_module(package), module)

def get_store(request):
    try:
        store_class = import_module_attr(conf.STORE)
    except ImportError:
        raise ImproperlyConfigured("OpenID store %r could not be imported" % conf.STORE)
    # The FileOpenIDStore requires a path to save the user files.
    if conf.STORE == 'openid.store.filestore.FileOpenIDStore':
        return store_class(conf.FILESTORE_PATH)
    return store_class()
