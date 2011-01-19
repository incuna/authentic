import urlparse
import os.path
import urllib
import httplib
import logging
import re
import datetime

import lasso
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from models import *
import models
import saml2utils
import saml11utils
import authentic2.utils

AUTHENTIC_STATUS_CODE_NS = "http://authentic.entrouvert.org/status_code/"
AUTHENTIC_STATUS_CODE_UNKNOWN_PROVIDER = AUTHENTIC_STATUS_CODE_NS + \
    "UnknownProvider"
AUTHENTIC_STATUS_CODE_MISSING_NAMEID= AUTHENTIC_STATUS_CODE_NS + \
    "MissingNameID"
AUTHENTIC_STATUS_CODE_MISSING_SESSION_INDEX = AUTHENTIC_STATUS_CODE_NS + \
    "MissingSessionIndex"
AUTHENTIC_STATUS_CODE_UNKNOWN_SESSION = AUTHENTIC_STATUS_CODE_NS + \
    "UnknownSession"
AUTHENTIC_STATUS_CODE_MISSING_DESTINATION = AUTHENTIC_STATUS_CODE_NS + \
    "MissingDestination"
AUTHENTIC_STATUS_CODE_INTERNAL_SERVER_ERROR = AUTHENTIC_STATUS_CODE_NS + \
    "InternalServerError"

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
        if request.META['CONTENT_TYPE'] in \
            ('application/x-www-form-urlencoded', 'multipart/form-data'):
            return 'POST'
        else:
            return 'SOAP'

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

asynchronous_bindings = [ lasso.SAML2_METADATA_BINDING_REDIRECT,
                lasso.SAML2_METADATA_BINDING_POST ]
soap_bindings = [ lasso.SAML2_METADATA_BINDING_SOAP ]
all_bindings = asynchronous_bindings + [ lasso.SAML2_METADATA_BINDING_SOAP ]

def get_saml2_metadata(request, metadata, idp_map=None, sp_map=None, options={}):
    metagen = saml2utils.Saml2Metadata(get_entity_id(request, metadata),
            url_prefix = get_base_path(request, metadata))
    if idp_map:
        metagen.add_idp_descriptor(idp_map, options)
    if sp_map:
        metagen.add_sp_descriptor(sp_map, options)
    return str(metagen)

def create_saml2_server(request, metadata, idp_map=None, sp_map=None, options={}):
    '''Create a lasso Server object for using with a profile'''
    server = lasso.Server.newFromBuffers(get_saml2_metadata(request, metadata,
        idp_map=idp_map, sp_map=sp_map, options=options),
        settings.SAML_PRIVATE_KEY)
    if not server:
        raise Exception('Cannot create LassoServer object')
    return server

def get_saml2_post_response(request):
    '''Extract the SAMLRequest field from the POST'''
    return request.POST.get(lasso.SAML2_FIELD_RESPONSE, '')

def get_saml2_post_request(request):
    '''Extract the SAMLRequest field from the POST'''
    return request.POST.get(lasso.SAML2_FIELD_REQUEST, '')

def get_saml2_query_request(request):
    return request.META.get('QUERY_STRING', '')

def get_saml2_soap_request(request):
    return get_soap_message(request)

def get_saml2_request_message_async_binding(request):
    '''Return SAMLv2 message whatever the HTTP binding used'''
    binding = get_http_binding(request)
    if binding == 'GET':
        return get_saml2_query_request(request)
    elif binding == 'POST':
        return get_saml2_post_request(request)
    else:
        raise Http404('This endpoint is only for asynchornous bindings')

def get_saml2_request_message(request):
    '''Return SAMLv2 message whatever the HTTP binding used'''
    binding = get_http_binding(request)
    if binding == 'GET':
        return get_saml2_query_request(request)
    elif binding == 'POST':
        return get_saml2_post_request(request)
    elif binding == 'SOAP':
        return get_saml2_soap_request(request)

def return_saml2_response(request, profile, title = ''):
    '''Finish your SAMLv2 views with this method to return a SAML
    response'''
    return return_saml2(request, profile, lasso.SAML2_FIELD_RESPONSE, title)

def return_saml2_request(request, profile, title = ''):
    '''Finish your SAMLv2 views with this method to return a SAML
    request'''
    return return_saml2(request, profile, lasso.SAML2_FIELD_REQUEST, title)

def return_saml2(request, profile, field_name, title = ''):
    '''Helper to handle SAMLv2 bindings to emit request and responses'''
    context_instance = RequestContext(request)
    if profile.msgBody:
        if profile.msgUrl:
            return render_to_response('saml/post_form.html',{
                        'title': title,
                        'url': profile.msgUrl,
                        'fieldname': field_name,
                        'body': profile.msgBody,
                        'relay_state': profile.msgRelayState },
                        context_instance=context_instance)
        return HttpResponse(profile.msgBody, mimetype = 'text/xml')
    elif profile.msgUrl:
        return HttpResponseRedirect(profile.msgUrl)
    else:
        raise TypeError('profile do not contain a response')

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
    options = { 'key': settings.SAML_SIGNING_KEY }
    metagen.add_idp_descriptor(map, options)
    return str(metagen)

def create_idff12_server(request, metadata):
    server = lasso.Server.newFromBuffers(get_idff12_metadata(request,
        metadata), settings.SAML_PRIVATE_KEY)
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

def return_idff12_response(request, profile, title = ''):
    '''Finish your ID-FFv1.2 views with this method to return a SAML
    response'''
    return return_saml2(request, profile, 'LARES', title)

def return_idff12_request(request, profile, title = ''):
    '''Finish your SAMLv2 views with this method to return a SAML
    request'''
    return return_saml2(request, profile, 'LAREQ', title)

# Helper method to handle profiles endpoints
# In the future we should move away from monolithic object (LassoIdentity and
# LassoSession) holding all the datas, to manipulate them at row Level with
# LibertyFederation and LibertyAssertion objects.

def load_federation(request, login, user = None):
    '''Load an identity dump from the database'''
    if not user:
        user = request.user
    try:
        q = LibertyIdentityDump.objects.get(user = user)
        login.setIdentityFromDump(q.identity_dump.encode('utf8'))
    except ObjectDoesNotExist:
        pass


def load_session(request, login, session_key = None):
    '''Load a session dump from the database'''
    if not session_key:
        session_key = request.session.session_key
    try:
        q = LibertySessionDump.objects.get(django_session_key = session_key)
        login.setSessionFromDump(q.session_dump.encode('utf8'))
    except ObjectDoesNotExist:
        pass

def save_federation(request, login, user = None):
    '''Save identity dump to database'''
    if not user:
        user = request.user
    if login.isIdentityDirty:
        q, creation = LibertyIdentityDump.objects.get_or_create(user = user)
        if login.identity:
            q.identity_dump = login.identity.dump()
        else:
            q.identity_dump = None
        q.save()

def save_session(request, login, session_key = None):
    '''Save session dump to database'''
    if not session_key:
        session_key = request.session.session_key
    if login.isSessionDirty:
        q, creation = LibertySessionDump.objects.get_or_create(
                django_session_key = session_key)
        if login.session:
            q.session_dump = login.session.dump()
        else:
            q.session_dump = None
        q.save()

def delete_session(request):
    '''Delete all liberty sessions for a django session'''
    all_sessions = LibertySessionDump.objects.get(django_session_key = request.session.session_key)
    try:
        all_sessions.delete()
    except:
        try:
            for s in all_sessions:
                s.delete()
        except:
            pass


def save_manage(request, manage):
    if not request or not manage:
        raise Exception('Cannot save manage dump')
    LibertyManageDump(django_session_key = request.session.session_key,
                    manage_dump = manage.dump()).save()

def get_manage_dump(request):
    if not request:
        raise Exception('Cannot get manage dump')
    d = LibertyManageDump.objects.filter(django_session_key = request.session.session_key)
    return d

def retrieve_metadata_and_create(request, provider_id, sp_or_idp):
    if not provider_id.startswith('http'):
        return None
    # Try the WKL
    try:
        metadata = urllib.urlopen(provider_id).read()
    except:
        logging.error('SAML metadata autoload: failure to retrieve metadata \
for entity id %r' % provider_id)
        return None
    try:
        metadata = unicode(metadata, 'utf8')
    except:
        logging.error('SAML metadata autoload: retrieved metadata \
for entity id %r is not UTF-8' % provider_id)
        return None
    p = LibertyProvider(metadata=metadata)
    try:
        p.clean()
    except ValidationError:
        logging.error('SAML metadata autoload: retrieved metadata \
for entity id %r are invalid' % provider_id)
        return None
    except:
        logging.exception('SAML metadata autoload: retrieved metadata validation raised an unknown exception')
        return None
    p.save()
    if sp_or_idp == 'sp':
        s = LibertyServiceProvider(liberty_provider=p, enabled=True, ask_user_consent=True)
        s.save()
    elif sp_or_idp == 'idp':
        raise NotImplementedError()
    return p

def load_provider(request, provider_id, server=None, sp_or_idp='sp'):
    '''Look up a provider in the database, and verify it handles wanted
       role be it sp or idp.

       Arguments:
       request -- the currently handled request
       provider_id -- the entity ID of the searched provider
       Keyword arguments:
       server -- a lasso.Server object into which to load the given provider
       sp_or_idp -- kind of the provider we are looking for, can be 'sp' or 'idp',
       default to 'sp'
    '''
    try:
        liberty_provider = LibertyProvider.objects.get(entity_id=provider_id)
    except LibertyProvider.DoesNotExist:
        autoload = getattr(settings, 'SAML_METADATA_AUTOLOAD', 'none')
        if autoload == 'sp' or autoload == 'both':
            liberty_provider = retrieve_metadata_and_create(request, provider_id, sp_or_idp)
            if not liberty_provider:
                return False
        else:
            return False
    if sp_or_idp == 'sp':
        try:
            service_provider = liberty_provider.service_provider
        except LibertyServiceProvider.DoesNotExist:
            return False
        if not service_provider.enabled:
            return False
        if server:
            server.addProviderFromBuffer(lasso.PROVIDER_ROLE_SP,
                    liberty_provider.metadata.encode('utf8'))
    elif sp_or_idp == 'idp':
        try:
            identity_provider = liberty_provider.identity_provider
        except LibertyIdentityProvider.DoesNotExist:
            return False
        if not identity_provider.enabled:
            return False
        if server:
            server.addProviderFromBuffer(lasso.PROVIDER_ROLE_IDP,
                    liberty_provider.metadata.encode('utf8'))
    else:
        raise Exception('unsupported option sp_or_idp = %r' % sp_or_idp)

    return liberty_provider

# Federation management
def add_federation(user, login=None, name_id=None):
    if not name_id:
        if not login:
            return None
        if not login.nameIdentifier:
            return None
        if not login.nameIdentifier.content or not login.nameIdentifier.nameQualifier:
            return None
        name_id=login.nameIdentifier
    qualifier = name_id.nameQualifier
    if not qualifier and login:
        qualifier = login.get_remoteProviderId()
    fed = LibertyFederation()
    fed.user = user
    fed.name_id_content = name_id.content
    fed.name_id_qualifier = qualifier
    fed.name_id_sp_name_qualifier = name_id.sPNameQualifier
    fed.name_id_format = name_id.format
    fed.save()
    return fed

def lookup_federation_by_name_identifier(name_id=None, profile=None):
    '''Try to find a LibertyFederation object for the given NameID or
       profile object.'''
    if not name_id:
        name_id = profile.nameIdentifier
    fed = LibertyFederation.objects.filter(name_id_content=name_id.content)
    if not fed:
        return None
    return fed[0]
    kwargs = models.nameid2kwargs(name_id)
    return LibertyFederation.objects.get(**kwargs)

# TODO: Does it happen that a user have multiple federation with a same idp? NO
def lookup_federation_by_user(user, qualifier):
    if not user or not qualifier:
        return None
    fed = LibertyFederation.objects.filter(user=user, name_id_qualifier=qualifier)
    if fed and fed.count()>1:
        # TODO: delete all but the last record
        raise Exception('Unconsistent federation record for %s' % ni)
    if not fed:
        return None
    return fed[0]

# List Idp providers - Use from display in templates
# WARNING: No way for multiple federation by user with a single IdP (is it a problem??)
def get_idp_list():
    return LibertyProvider.objects.exclude(identity_provider=None) \
            .values('entity_id','name')

def get_idp_list_sorted():
    return LibertyProvider.objects.exclude(identity_provider=None) \
            .order_by('name').values('entity_id','name')

def get_idp_user_federated_list(request):
    user = request.user
    if request.user.is_anonymous():
        return None
    providers_list = get_idp_list()
    p_list = []
    for p in providers_list:
        fed = lookup_federation_by_user(user, p.entity_id)
        if fed:
            p_list.append(p)
    return p_list

def get_idp_user_not_federated_list(request):
    user = request.user
    if request.user.is_anonymous():
        return None
    providers_list = get_idp_list()
    p_list = []
    for p in providers_list:
        fed = lookup_federation_by_user(user, p.entity_id)
        if not fed:
            p_list.append(p)
    return p_list

# The session_index is the "session on the IdP" identifiers
# One identifier is dedicated for each sp for each user session 
# to not be a factor of linkability between sp
# (like the nameId dedicated for each sp)
# A same user IdP session is thus made of as many session index as SP having received an auth a8n
# The session index is only useful to maintain 
# the coherence between the sessions on the IdP and on the SP
# for the global logout:
# If one session is broken somewhere, when a session is restablished there
# it can be linked to other remaining session
# and then make feasible the global logout
# The table entry for the liberty session should be removed at the logout
# TODO: Xpath search of sessionIndex
def maintain_liberty_session_on_service_provider(request, login):
    if not login:
        return False
    # 1. Retrieve this user federation
    fed = lookup_federation_by_name_identifier(profile=login)
    if not fed:
        return False
    # 2.a Retrieve a liberty session with the session index and this federation
    try:
        s = LibertySessionSP.objects.get(federation=fed, session_index=login.response.assertion[0].authnStatement[0].sessionIndex)
        # Liberty Session already existing
        # If the local session registered is different: updated
        # It would mean that the local session was broken
        # and not the distant one
        s.django_session_key = request.session.session_key
        s.save()
        return True
    except:
        pass
    # 2.b Retrieve a liberty session with the django session identifier and this federation
    try:
        s = LibertySessionSP.objects.get(federation=fed, django_session_key=request.session.session_key)
        # Local session already existing
        # If the index session registered is different: updated
        # It would mean that the distant session was broken
        # and not the local one
        s.session_index = login.response.assertion[0].authnStatement[0].sessionIndex
        s.save()
        return True
    except:
        pass
    # 2.c Create a new Liberty Session
    try:
        s = LibertySessionSP()
        s.federation = fed
        s.django_session_key = request.session.session_key
        s.session_index = login.session.getAssertions()[0].authnStatement[0].sessionIndex
        s.save()
        return True
    except:
        return False
    return False

def get_session_index(request):
    if not request:
        return None
    try:
        s = LibertySessionSP.objects.get(django_session_key=request.session.session_key)
        return s.session_index
    except:
        return None

def remove_liberty_session_sp(request):
    if not request:
        return None
    try:
        ss = LibertySessionSP.objects.filter(django_session_key=request.session.session_key)
        for s in ss:
            s.delete()
    except:
        return None

def get_provider_of_active_session(request):
    if not request:
        return None
    try:
        s = LibertySessionSP.objects.get(django_session_key=request.session.session_key)
        p = LibertyProvider.objects.get(entity_id=s.federation.name_id_qualifier)
        return p
    except:
        return None

def get_provider_of_active_session_name(request):
    if not request:
        return None
    p = get_provider_of_active_session(request)
    if not p:
        return None
    from urlparse import urlparse
    return urlparse(p.entity_id)[1]

class SOAPException(Exception):
    url = None
    def __init__(self, url):
        self.url = url

def soap_call(url, msg, client_cert = None):
    if url.startswith('http://'):
        host, query = urllib.splithost(url[5:])
        conn = httplib.HTTPConnection(host)
    else:
        host, query = urllib.splithost(url[6:])
        conn = httplib.HTTPSConnection(host,
                key_file = client_cert, cert_file = client_cert)
    try:
        conn.request('POST', query, msg, {'Content-Type': 'text/xml'})
        response = conn.getresponse()
    except Exception, err:
        logging.error('SOAP error (on %s): %s' % (url, err))
        raise SOAPException(url)
    try:
        data = response.read()
    except Exception, err:
        logging.error('SOAP error (on %s): %s' % (url, err))
        raise SOAPException(url)
    conn.close()
    if response.status not in (200, 204): # 204 ok for federation termination
        logging.warning('SOAP error (%s) (on %s)' % (response.status, url))
        raise SOAPException(url)
    return data

def send_soap_request(request, profile):
    '''Send the SOAP request hold by the profile'''
    if not profile.msgUrl or not profile.msgBody:
        raise SOAPException('Missing body or url')
    p = LibertyProvider.objects.get(entity_id=profile.remoteProviderId)
    return soap_call(profile.msgUrl, profile.msgBody, p.ssl_certificate)


def set_saml2_response_responder_status_code(response, code):
    response.status = lasso.Samlp2Status()
    response.status.statusCode = lasso.Samlp2StatusCode()
    response.status.statusCode.value = lasso.SAML2_STATUS_CODE_RESPONDER
    response.status.statusCode.statusCode = lasso.Samlp2StatusCode()
    response.status.statusCode.statusCode.value = code

__root_refererer_re = re.compile('^(https?://[^/]*/?)')
def error_page(request, message, back = None):
    '''View that show a simple error page to the user with a back link.

         back - url for the back link, if None, return to root of the referer
                or the local root.
    '''
    logging.error('Showing message %r on an error page' % message)
    if back is None:
        referer = request.META.get('HTTP_REFERER')
        if referer:
            root_referer = __root_refererer_re.match(referer)
            if root_referer:
                back = root_referer.group(1)
        if back is None:
            back = '/'
    return render_to_response('error.html', {'msg': message, 'back': back},
            context_instance=RequestContext(request))

def soap_fault(request, faultcode='soap:Client', faultstring=None):
    if faultstring:
        faultstring = '\n        <faultstring>%s</faultstring>\n' % faultstring
    content = '''<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body><soap:Fault>
       <faultcode>%(faultcode)s</faultcode>%(faultstring)s
    </soap:Fault></soap:Body>
</soap:Envelope>''' % locals()
    return HttpResponse(content, mimetype = "text/xml")

def iso8601_to_datetime(date_string):
    '''Convert a string formatted as an ISO8601 date into a time_t value.

       This function ignores the sub-second resolution'''
    m = re.match(r'(\d+-\d+-\d+T\d+:\d+:\d+)(?:\.\d+)?Z$', date_string)
    if not m:
        raise ValueError('Invalid ISO8601 date')
    tm = time.strptime(m.group(1)+'Z', "%Y-%m-%dT%H:%M:%SZ")
    return datetime.datetime.fromtimestamp(time.mktime(tm))
