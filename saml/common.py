import urlparse
import os.path
import lasso
import saml2utils
import saml11utils
from django.conf import settings
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from models import *

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

def get_base_path(request, metadata):
    '''Get endpoints base path given metadata path
    '''
    path = urlparse.urlparse(metadata).path
    return request.build_absolute_uri(os.path.dirname(path))

def get_entity_id(request, metadata):
    '''Return the EntityID, given metadata absolute path
    '''
    return request.build_absolute_uri(metadata)

def get_saml2_metadata(request, metadata):
    metagen = saml2utils.Saml2Metadata(get_entity_id(request, metadata),
            url_prefix = get_base_path(request, metadata))
    synchronous_bindings = [ lasso.SAML2_METADATA_BINDING_REDIRECT,
                    lasso.SAML2_METADATA_BINDING_POST ]
    map = (('SingleSignOnService', synchronous_bindings , '/sso'),)
    options = { 'signing_key': SAML_PRIVATE_KEY }
    metagen.add_idp_descriptor(map, options)
    return str(metagen)

def create_saml2_server(request, metadata):
    '''Create a lasso Server object for using with a profile'''
    server = lasso.Server.newFromBuffers(get_saml2_metadata(request, metadata),
            SAML_PRIVATE_KEY)
    if not server:
        raise Exception('Cannot create LassoServer object')
    return server

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
def get_idff12_metadata(request, metadata):
    '''Produce SAMLv1.1 metadata for our ID-FF 1.2 IdP

      This method only works with request pointing to an endpoint'''

    metagen = saml11utils.Saml11Metadata(get_entity_id(request, metadata),
            url_prefix = get_base_path(request, metadata),
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

def create_idff12_server(request, metadata):
    server = lasso.Server.newFromBuffers(get_idff12_metadata(request, metadata),
            SAML_PRIVATE_KEY)
    if not server:
        raise Exception('Cannot create LassoServer object')
    return server

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

def return_saml_soap_response(profile):
    return HttpResponse(profile.msgBody, mimetype = 'text/xml')

def return_idff12_response(profile, title = ''):
    '''Finish your ID-FFv1.2 views with this method to return a SAML
    response'''
    return return_saml2(profile, 'LARES', title)

def return_idff12_request(profile, title = ''):
    '''Finish your SAMLv2 views with this method to return a SAML
    request'''
    return return_saml2(profile, 'LAREQ', title)

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
        return return_saml_soap_response(profile)
    elif profile.msgUrl:
        return HttpResponseRedirect(profile.msgUrl)
    else:
        return TypeError('profile do not contain a response')

# Helper method to handle profiles endpoints
# In the future we should move away from monolithic object (LassoIdentity and
# LassoSession) holding all the datas, to manipulate them at row Level with
# LibertyFederation and LibertyAssertion objects.

def load_federation(request, login, user = None):
    '''Load an identity dump from the database'''
    if not user:
        user = request.user
    q = LibertyIdentityDump.objects.filter(user = user)
    if not q:
        return
    login.setIdentityFromDump(q[0].identity_dump)

def load_session(request, login, session_key = None):
    '''Load a session dump from the database'''
    if not session_key:
        session_key = request.session.session_key
    q = LibertySessionDump.objects.filter(django_session_key = session_key)
    if not q:
        return
    login.setSessionFromDump(q[0].session_dump)

def save_federation(request, login, user = None):
    '''Save identity dump to database'''
    if not user:
        user = request.user
    if login.isIdentityDirty:
        q = LibertyIdentityDump.objects.filter(user = user)
        if q:
            if login.identity:
                q[0].identity_dump = login.identity.dump()
            else:
                q[0].identity_dump = None
            q[0].save()
        elif login.identity:
            LibertyIdentityDump(user = request.user,
                    identity_dump = login.identity.dump()).save()

def save_session(request, login, session_key = None):
    '''Save session dump to database'''
    if not session_key:
        session_key = request.session.session_key
    if login.isSessionDirty:
        q = LibertySessionDump.objects.filter(
                django_session_key = session_key)
        if q:
            if login.session:
                q[0].session_dump = login.session.dump()
            else:
                q[0].session_dump = None
            q[0].save()
        elif login.session:
            LibertySessionDump(django_session_key = request.session.session_key,
                    session_dump = login.session.dump()).save()

# TODO: handle autoloading of metadatas
def load_provider(request, login, provider_id, sp_or_idp = 'sp'):
    '''Look up a provider in the database, and verify it handles wanted
       role be it sp or idp.
    '''
    liberty_provider = LibertyProvider.objects.get(entity_id = provider_id)
    if not liberty_provider:
        return False
    if sp_or_idp == 'sp':
        try:
            service_provider = liberty_provider.service_provider
        except LibertyServiceProvider.DoesNotExist:
            return False
        if not service_provider.enabled:
            return False
        login.server.addProviderFromBuffer(lasso.PROVIDER_ROLE_SP,
                liberty_provider.metadata.read())
    elif sp_or_idp == 'idp':
        try:
            identity_provider = liberty_provider.identity_provider
        except LibertyIdentityProvider.DoesNotExist:
            return False
        if not identity_provider.enabled:
            return False
        login.server.addProviderFromBuffer(lasso.PROVIDER_ROLE_IDP,
                liberty_provider.metadata.read())
    else:
        raise Exception('unsupported option sp_or_idp = %r' % sp_or_idp)

    return liberty_provider
