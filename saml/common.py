import lasso
import saml2utils
import saml11utils
from django.conf import settings
from django.http import HttpResponseRedirect


SAML_PRIVATE_KEY = settings.SAML_PRIVATE_KEY

def get_http_binding(request):
    if request.method == 'GET':
        return 'GET'
    elif request.method == 'POST':
        # disambiguate SOAP and form POST
        if request.META.get('CONTENT_TYPE') == 'text/xml':
            return 'SOAP'
        else:
            return 'POST'

# SAMLv2 methods

def get_saml2_metadata(request):
    # FIXME: find the base URL with a better method than that
    base = 'http://' + request.get_host() + '/idp/saml2'
    metagen = saml2utils.Saml2Metadata(base + '/metadata', url_prefix = base)
    synchronous_bindings = [ lasso.SAML2_METADATA_BINDING_REDIRECT,
                    lasso.SAML2_METADATA_BINDING_POST ]
    map = (('SingleSignOnService', synchronous_bindings , '/sso'),)
    options = { 'signing_key': SAML_PRIVATE_KEY }
    metagen.add_idp_descriptor(map, options)
    return str(metagen)

def create_saml2_server(request):
    '''Create a lasso Server object for using with a profile'''
    return lasso.Server.newFromBuffers(get_saml2_metadata(request),
            SAML_PRIVATE_KEY)

def get_saml2_post_request(request):
    '''Extract the SAMLRequest field from the POST'''
    return request.POST.get(lasso.SAML2_FIELD_REQUEST, '')

def get_saml2_query_request(request):
    return request.META.get('QUERY_STRING', '')

def get_saml2_soap_request(request):
    return request.raw_post_data

def get_saml2_request_message(request):
    '''Return SAMLv2 message whatever the HTTP binding used'''
    binding = get_http_binding(request)
    if binding == 'GET':
        return get_saml2_query_request(request)
    elif binding == 'POST':
        return get_saml2_post_request(request)
    elif binding == 'SOAP':
        return get_saml2_soap_request(request)

def get_saml2_response(profile):
    if profile.msgBody:
        if profile.msgUrl:
            message = 'SAML POST response binding not implemented'
            return NotImplementedError(message)
        return HttpResponse(profile.msgBody, mimetype = 'text/xml')
    elif profile.msgUrl:
        return HttpResponseRedirect(profile.msgUrl)
    else:
        return TypeError('profile do not contain a response')

# ID-FF 1.2 methods
def get_idff12_metadata(request):
    # FIXME: find the base URL with a better method than that
    base = 'http://' + request.get_host() + '/idp/idff12'
    metagen = saml11utils.Saml11Metadata(base + '/metadata', url_prefix = base, protocol_support_enumeration = [ lasso.LIB_HREF ])
    sso_protocol_profiles = [
        lasso.LIB_PROTOCOL_PROFILE_BRWS_ART,
        lasso.LIB_PROTOCOL_PROFILE_BRWS_POST,
        lasso.LIB_PROTOCOL_PROFILE_BRWS_LECP ]
    map = {
            'SoapEndpoint': '/soap',
            'SingleSignOn': (('/sso',), sso_protocol_profiles)
          }
    options = { 'signing_key': SAML_PRIVATE_KEY }
    metagen.add_idp_descriptor(map, options)
    return str(metagen)

def create_idff12_server(request):
    return lasso.Server.newFromBuffers(get_idff12_metadata(request),
            SAML_PRIVATE_KEY)

def get_idff12_post_request(request):
    '''Return a SAML 1.1 request transmitted through a POST request'''
    return request.POST.get('LAREQ')

get_idff12_query_request = get_saml2_query_request

def get_idff12_request_message(request):
    binding = get_http_binding(request)
    if binding == 'GET':
        return get_idff12_query_request(request)
    elif binding == 'POST':
        return get_idff12_post_request(request)

