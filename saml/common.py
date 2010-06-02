import lasso
from django.conf import settings
from django.http import HttpResponseRedirect

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
    options = { 'signing_key': private_key }
    metagen.add_idp_descriptor(map, options)
    return str(metagen)

def create_saml2_server(request):
    '''Create a lasso Server object for using with a profile'''
    return lasso.Server.newFromBuffers(get_saml2_metadata(request), private_key)

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
            return NotImplementedError('SAML POST response binding not implemented')
        return HttpResponse(profile.msgBody, mimetype = 'text/xml')
    elif profile.msgUrl:
        return HttpResponseRedirect(profile.msgUrl)
    else:
        return TypeError('profile do not contain a response')

# ID-FF 1.2 methods
