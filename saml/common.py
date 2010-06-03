import urlparse
import os.path
import lasso
import saml2utils
import saml11utils
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

SAML_PRIVATE_KEY = settings.SAML_PRIVATE_KEY

def get_soap_message(request, on_error_raise = True):
    '''Verify that POST content looks like a SOAP message and returns it'''
    if request.method != 'POST' or \
            request.META['CONTENT_TYPE'] != 'text/xml':
       if on_error_raise:
           raise Http404(_('Only SOAP messages here'))
       else:
           return None
    return request.raw_post_data

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

def get_base_path(request):
    full_path = request.get_full_path()
    path = urlparse.urlparse(full_path).path
    return request.build_absolute_uri(os.path.dirname(path))

def get_entity_id(request):
    '''Return the EntityID, request must points to an endpoint handler'''
    # FIXME: find the base URL with a better method than that
    path = get_base_path(request)
    return path + '/metadata'

def get_saml2_metadata(request):
    metagen = saml2utils.Saml2Metadata(get_entity_id(request),
            url_prefix = get_base_path(request))
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

def return_saml2_response(profile, title = ''):
    '''Finish your SAMLv2 views with this method to return a SAML
    response'''
    return return_saml2(profile, lasso.SAML2_FIELD_RESPONSE, title)

def return_saml2_request(profile, title = ''):
    '''Finish your SAMLv2 views with this method to return a SAML
    request'''
    return return_saml2(profile, lasso.SAML2_FIELD_REQUEST, title)

def return_saml2(profile, field_name, title = ''):
    '''Helper to handle SAMLv2 bindings to emit request and responses'''
    if profile.msgBody:
        if profile.msgUrl:
            render_to_response('saml/post_form.html',{
                        'title': title,
                        'url': profile.msgUrl,
                        'fieldname': field_name,
                        'body': profile.msgBody,
                        'relay_state': profile.msgRelayState })
        return HttpResponse(profile.msgBody, mimetype = 'text/xml')
    elif profile.msgUrl:
        return HttpResponseRedirect(profile.msgUrl)
    else:
        return TypeError('profile do not contain a response')

# ID-FF 1.2 methods
def get_idff12_metadata(request):
    '''Produce SAMLv1.1 metadata for our ID-FF 1.2 IdP

      This method only works with request pointing to an endpoint'''
    metagen = saml11utils.Saml11Metadata(get_entity_id(request),
            url_prefix = get_base_path(request),
            protocol_support_enumeration = [ lasso.LIB_HREF ])
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

def return_idff12_response(profile, title = ''):
    '''Finish your ID-FFv1.2 views with this method to return a SAML
    response'''
    return return_saml2(profile, lasso.SAML2_FIELD_RESPONSE, title)

def return_idff12_request(profile, title = ''):
    '''Finish your SAMLv2 views with this method to return a SAML
    request'''
    return return_saml2(profile, lasso.SAML2_FIELD_REQUEST, title)

def return_idff12(profile, field_name, title = ''):
    '''Helper to handle SAMLv2 bindings to emit request and responses'''
    if profile.msgBody:
        if profile.msgUrl:
            render_to_response('saml/post_form.html',{
                        'title': title,
                        'url': profile.msgUrl,
                        'fieldname': field_name,
                        'body': profile.msgBody,
                        'relay_state': profile.msgRelayState })
        return HttpResponse(profile.msgBody, mimetype = 'text/xml')
    elif profile.msgUrl:
        return HttpResponseRedirect(profile.msgUrl)
    else:
        return TypeError('profile do not contain a response')
