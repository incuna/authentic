# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 fdm=indent : */
# some code from http://www.djangosnippets.org/snippets/310/ by simon
# and from examples/djopenid from python-openid-2.2.4

from openid.extensions import sreg
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.http import HttpResponse

import conf

def oresponse_to_response(server, oresponse):
    webresponse = server.encodeResponse(oresponse)
    response = HttpResponse(webresponse.body)
    response.status_code = webresponse.code
    for key, value in webresponse.headers.items():
        response[key] = value
    return response

def import_module_attr(path):
    package, module = path.rsplit('.', 1)
    return getattr(import_module(package), module)

def add_sreg_data(request, orequest, oresponse):
    sreg_req = sreg.SRegRequest.fromOpenIDRequest(orequest)
    sreg_resp = sreg.SRegResponse.extractResponse(sreg_req, {
        'email': request.user.email,
        'nickname': request.user.username,
        'fullname': request.user.get_full_name(),
    })
    oresponse.addExtension(sreg_resp)

def get_store(request):
    try:
        store_class = import_module_attr(conf.STORE)
    except ImportError:
        raise ImproperlyConfigured("OpenID store %r could not be imported" % conf.STORE)
    # The FileOpenIDStore requires a path to save the user files.
    if conf.STORE == 'openid.store.filestore.FileOpenIDStore':
        return store_class(conf.FILESTORE_PATH)
    return store_class()
