import os.path
import time
import xml.etree.ElementTree as etree
import hashlib
import binascii
import base64

import lasso
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from fields import *

# TODO: add other name formats with lasso next release
ATTRIBUTE_VALUE_FORMATS = (
        (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, 'SAMLv2 URI'),)

class LibertyAttributeMap(models.Model):
    name = models.CharField(max_length = 40, unique = True)
    def __unicode__(self):
        return self.name

class LibertyAttributeMapping(models.Model):
    source_attribute_name = models.CharField(max_length = 40)
    attribute_value_format = models.URLField(choices = ATTRIBUTE_VALUE_FORMATS)
    attribute_name = models.CharField(max_length = 40)
    map = models.ForeignKey(LibertyAttributeMap)

def metadata_validator(meta):
    provider=lasso.Provider.newFromBuffer(lasso.PROVIDER_ROLE_ANY, meta.encode('utf8'))
    if not provider:
        raise ValidationError(_('Bad metadata file'))
XML_NS = 'http://www.w3.org/XML/1998/namespace'

def get_lang(etree):
    return etree.get('{%s}lang' % XML_NS)

def ls_find(ls, value):
    try:
        return ls.index(value)
    except ValueError:
        return -1

def get_prefered_content(etrees, languages = [None, 'en']):
    '''Sort XML nodes by their xml:lang attribute using languages as the
    ascending partial order of language identifiers

       Default is to prefer english, then no lang declaration, to anything
       else.
    '''
    best = None
    for tree in etrees:
        if best is not None:
            i = ls_find(languages, get_lang(tree))
            if i > best_score:
                best = tree
                best_score = ls_find(languages, get_lang(tree))
        else:
            best = tree
            best_score = ls_find(languages, get_lang(tree))
    return best.text

def organization_name(provider):
    '''Extract an organization name from a SAMLv2 metadata organization XML
       fragment.
    '''
    try:
        organization_xml = provider.organization
        organization = etree.XML(organization_xml)
        o_display_name = organization.findall('{%s}OrganizationDisplayName' %
                lasso.SAML2_METADATA_HREF)
        if o_display_name:
            return get_prefered_content(o_display_name)
        o_name = organization.findall('{%s}OrganizationName' %
                lasso.SAML2_METADATA_HREF)
        if o_name:
            return get_prefered_content(o_name)
    except:
        return provider.providerId
    else:
        return provider.providerId

class LibertyProvider(models.Model):
    entity_id = models.URLField(unique = True)
    entity_id_sha1 = models.CharField(max_length = 40, blank=True)
    name = models.CharField(max_length = 40, unique = True,
            help_text = _("Internal nickname for the service provider"),
            blank = True)
    protocol_conformance = models.IntegerField(max_length = 10,
            choices = ((0, 'SAML 1.0'),
                       (1, 'SAML 1.1'),
                       (2, 'SAML 1.2'),
                       (3, 'SAML 2.0')))
    metadata = models.TextField(validators = [ metadata_validator ])
    # All following field must be PEM formatted textual data
    public_key = models.TextField(blank=True)
    ssl_certificate = models.TextField(blank=True)
    ca_cert_chain = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        '''Update the SHA1 hash of the entity_id when saving'''
        if self.protocol_conformance == 3:
            self.entity_id_sha1 = hashlib.sha1(self.entity_id).hexdigest()
        super(LibertyProvider, self).save(*args, **kwargs)

    @classmethod
    def get_provider_by_samlv2_artifact(cls, artifact):
        '''Find a provider whose SHA-1 hash of its entityID is the 5-th to the
           25-th byte of the given artifact'''
        try:
            artifact = base64.b64decode(artifact)
        except:
            raise ValueError('Artifact is not a base64 encoded value')
        entity_id_sha1 = artifact[4:24]
        entity_id_sha1 = binascii.hexlify(entity_id_sha1)
        try:
            return cls.objects.get(entity_id_sha1=entity_id_sha1)
        except cls.DoesNotExist:
            return None

    def clean(self):
        super(LibertyProvider, self).clean()
        if self.metadata:
            p = lasso.Provider.newFromBuffer(lasso.PROVIDER_ROLE_ANY, self.metadata.encode('utf8'))
            if p:
                self.entity_id = p.providerId
                if not self.name:
                    self.name = organization_name(p)
                self.protocol_conformance = p.protocolConformance
        else:
            print 'coin'

# TODO: Remove this in LibertyServiceProvider
ASSERTION_CONSUMER_PROFILES = (
        ('meta', _('Use the default from the metadata file')),
        ('art', _('Artifact binding')),
        ('post', _('Post binding')))

DEFAULT_NAME_ID_FORMAT = 'none'

# Supported name id formats
NAME_ID_FORMATS = {
        'none': { 'caption': _('None'),
            'samlv2': None,
            'idff12': None },
        'persistent': { 'caption': _('Persistent'),
            'samlv2': lasso.SAML2_NAME_IDENTIFIER_FORMAT_PERSISTENT,
            'idff12': lasso.LIB_NAMEID_POLICY_TYPE_FEDERATED },
        'transient': { 'caption': _("Transient"),
            'samlv2': lasso.SAML2_NAME_IDENTIFIER_FORMAT_TRANSIENT,
            'idff12': lasso.LIB_NAMEID_POLICY_TYPE_ONE_TIME },
        'email': { 'caption': _("Email (only supported by SAMLv2)"),
            'samlv2': lasso.SAML2_NAME_IDENTIFIER_FORMAT_EMAIL,
            'idff12': None }}

NAME_ID_FORMATS_CHOICES = \
        tuple([(x, y['caption']) for x, y in NAME_ID_FORMATS.iteritems()])

ACCEPTED_NAME_ID_FORMAT_LENGTH = \
        sum([len(x) for x, y in NAME_ID_FORMATS.iteritems()]) + \
        len(NAME_ID_FORMATS) - 1

def saml2_urn_to_nidformat(urn):
    for x, y in NAME_ID_FORMATS.iteritems():
        if y['samlv2'] == urn:
            return x
    return None

def nidformat_to_saml2_urn(key):
    return NAME_ID_FORMATS.get(key, {}).get('samlv2')

def nidformat_to_idff12_urn(key):
    return NAME_ID_FORMATS.get(key, {}).get('idff12')

# TODO: The IdP must look to the preferred binding order for sso in the SP metadata (AssertionConsumerService)
# expect if the protocol for response is defined in the request (ProtocolBinding attribute)
class LibertyServiceProvider(models.Model):
    liberty_provider = models.OneToOneField(LibertyProvider,
            primary_key = True, related_name = 'service_provider')
    enabled = models.BooleanField(verbose_name = _('Enabled'))
    prefered_assertion_consumer_binding = models.CharField(
            default = 'meta',
            max_length = 4, choices = ASSERTION_CONSUMER_PROFILES)
    encrypt_nameid = models.BooleanField(verbose_name = _("Encrypt NameID"))
    encrypt_assertion = models.BooleanField(
            verbose_name = _("Encrypt Assertion"))
    authn_request_signed = models.BooleanField(
            verbose_name = _("AuthnRequest signed"))
    idp_initiated_sso = models.BooleanField(
            verbose_name = _("Allow IdP initiated SSO"))
    # Mapping to use to produce attributes in the assertions or in Attribute
    # requests
    attribute_map = models.ForeignKey(LibertyAttributeMap,
            related_name = "service_providers",
            blank = True, null = True)
    # XXX: format in the metadata file, should be suffixed with a star to mark
    # them as special
    default_name_id_format = models.CharField(max_length = 20,
            default = DEFAULT_NAME_ID_FORMAT,
            choices = NAME_ID_FORMATS_CHOICES)
    accepted_name_id_format = MultiSelectField(
            max_length=ACCEPTED_NAME_ID_FORMAT_LENGTH,
            blank=True, choices=NAME_ID_FORMATS_CHOICES)
    # TODO: add clean method which checks that the LassoProvider we can create
    # with the metadata file support the SP role
    # i.e. provider.roles & lasso.PROVIDER_ROLE_SP != 0
    ask_user_consent = models.BooleanField(
        verbose_name = _('Ask user for consent when creating a federation'), default = False)

# According to: saml-profiles-2.0-os
# The HTTP Redirect binding MUST NOT be used, as the response will typically exceed the URL length permitted by most user agents.
BINDING_SSO_IDP = (
    (lasso.SAML2_METADATA_BINDING_ARTIFACT, _('Artifact binding')),
    (lasso.SAML2_METADATA_BINDING_POST, _('POST binding'))
)
HTTP_METHOD = (
    (lasso.HTTP_METHOD_REDIRECT, _('Redirect binding')),
    (lasso.HTTP_METHOD_SOAP, _('SOAP binding'))
)

USER_CONSENT = (
    ('urn:oasis:names:tc:SAML:2.0:consent:unspecified', _('Unspecified')),
    ('urn:oasis:names:tc:SAML:2.0:consent:obtained', _('Obtained')),
    ('urn:oasis:names:tc:SAML:2.0:consent:prior', _('Prior')),
    ('urn:oasis:names:tc:SAML:2.0:consent:current-explicit', _('Explicit')),
    ('urn:oasis:names:tc:SAML:2.0:consent:current-implicit', _('Implicit')),
    ('urn:oasis:names:tc:SAML:2.0:consent:unavailable', _('Unavailable')),
    ('urn:oasis:names:tc:SAML:2.0:consent:inapplicable', _('Inapplicable'))
)

# TODO: The choice for requests must be restricted by the IdP metadata
# The SP then chooses the binding in this list.
# For response, if the requester uses a (a)synchronous binding, the responder uses the same.
# However, the responder can choose which asynchronous binding it employs.
class LibertyIdentityProvider(models.Model):
    liberty_provider = models.OneToOneField(LibertyProvider,
            primary_key = True, related_name = 'identity_provider')
    enabled = models.BooleanField(verbose_name = _('Enabled'))
    enable_following_policy = models.BooleanField(verbose_name = \
        _('The following options policy will apply except if the policy for all identity provider is defined.'))
    no_nameid_policy = models.BooleanField(
            verbose_name = _("Do not send a nameId Policy"))
    requested_name_id_format = models.CharField(max_length = 20,
            default = DEFAULT_NAME_ID_FORMAT,
            choices = NAME_ID_FORMATS_CHOICES)
    allow_create = models.BooleanField(
            verbose_name = _("Allow IdP to create an identity"))
    enable_binding_for_sso_response = models.BooleanField(
            verbose_name = _('Binding for Authnresponse (taken from metadata by the IdP if not enabled)'))
    binding_for_sso_response = models.CharField(
            max_length = 60, choices = BINDING_SSO_IDP,
            verbose_name = '',
            default = lasso.SAML2_METADATA_BINDING_ARTIFACT)
    enable_http_method_for_slo_request = models.BooleanField(
            verbose_name = _('HTTP method for single logout request (taken from metadata if not enabled)'))
    http_method_for_slo_request = models.IntegerField(
            max_length = 60, choices = HTTP_METHOD,
            verbose_name = '',
            default = lasso.HTTP_METHOD_REDIRECT)
    enable_http_method_for_defederation_request = models.BooleanField(
            verbose_name = _('HTTP method for federation termination request (taken from metadata if not enabled)'))
    http_method_for_defederation_request = models.IntegerField(
            max_length = 60, choices = HTTP_METHOD,
            verbose_name = '',
            default = lasso.HTTP_METHOD_SOAP)
    user_consent = models.CharField(
            max_length = 60, choices = USER_CONSENT,
            verbose_name = _("Ask user consent"),
            default = 'urn:oasis:names:tc:SAML:2.0:consent:current-implicit')
    want_force_authn_request = models.BooleanField(
            verbose_name = _("Force authentication"))
    want_is_passive_authn_request = models.BooleanField(
            verbose_name = _("Passive authentication"))
    want_authn_request_signed = models.BooleanField(
            verbose_name = _("Want AuthnRequest signed"))
    # Mapping to use to get User attributes from the assertion
    attribute_map = models.ForeignKey(LibertyAttributeMap,
            related_name = "identity_providers",
            blank = True, null = True)
    # TODO: add clean method which checks that the LassoProvider we can create
    # with the metadata file support the IDP role
    # i.e. provider.roles & lasso.PROVIDER_ROLE_IDP != 0


# Transactional models
class LibertyIdentityDump(models.Model):
    '''Store lasso identity dump

       Should be replaced in the future by direct reference to LassoFederation
       objects'''
    user = models.ForeignKey(User, unique = True)
    identity_dump = models.TextField(blank = True)

class LibertySessionDump(models.Model):
    '''Store lasso session object dump.

       Should be replaced in the future by direct references to known
       assertions through the LibertySession object'''
    django_session_key = models.CharField(max_length = 40)
    session_dump = models.TextField(blank = True)

class LibertyManageDump(models.Model):
    '''Store lasso manage dump

       Should be replaced in the future by direct reference to ?
       objects'''
    django_session_key = models.CharField(max_length = 40)
    manage_dump = models.TextField(blank = True)

class LibertyArtifact(models.Model):
    """Store an artifact and the associated XML content"""
    creation = models.DateTimeField(auto_now_add=True)
    artifact = models.CharField(max_length = 40, primary_key = True)
    content = models.TextField()
    django_session_key = models.CharField(max_length = 40)
    provider_id = models.CharField(max_length = 80)

def nameid2kwargs(name_id):
    return { 'name_id_qualifier': name_id.nameQualifier,
        'name_id_sp_name_qualifier': name_id.spNameQualifier,
        'name_id_content': name_id.content,
        'name_id_format': name_id.format }

class LibertyAssertion(models.Model):
    assertion_id = models.CharField(max_length = 50)
    provider_id = models.CharField(max_length = 80)
    session_index = models.CharField(max_length = 80, )
    assertion = models.TextField()
    creation = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        saml2_assertion = kwargs.pop('saml2_assertion', None)
        if saml2_assertion:
            kwargs['assertion_id'] = saml2_assertion.id
            kwargs['session_index'] = \
                    saml2_assertion.authnStatement[0].sessionIndex
            kwargs['assertion'] = saml2_assertion.exportToXml()
        models.Model.__init__(self, *args, **kwargs)

class LibertyFederation(models.Model):
    """Store a federation, i.e. an identifier shared with another provider, be
       it IdP or SP"""
    user = models.ForeignKey(User)
    idp_id = models.CharField(max_length=80)
    sp_id = models.CharField(max_length=80)
    name_id_qualifier = models.CharField(max_length = 150,
            verbose_name = "NameQualifier", blank=True, null=True)
    name_id_format = models.CharField(max_length = 100,
            verbose_name = "NameIDFormat", blank=True, null=True)
    name_id_content = models.CharField(max_length = 100,
            verbose_name = "NameID")
    name_id_sp_name_qualifier = models.CharField(max_length = 100,
            verbose_name = "SPNameQualifier", blank=True, null=True)
    name_id_sp_provided_id = models.CharField(max_length=100,
            verbose_name="SPProvidedID", blank=True, null=True)

    def __init__(self, *args, **kwargs):
        saml2_assertion = kwargs.pop('saml2_assertion', None)
        if saml2_assertion:
            name_id = saml2_assertion.subject.nameID
            kwargs.update(nameid2kwargs(name_id))
        models.Model.__init__(self, *args, **kwargs)

    class Meta:
        verbose_name = _("Liberty federation")
        verbose_name_plural = _("Liberty federations")
        # XXX: To allow shared-federation (multiple-user with the same
        # federation), add user to this list
        unique_together = (("name_id_qualifier", "name_id_format",
            "name_id_content", "name_id_sp_name_qualifier"))

class LibertySession(models.Model):
    """Store the link between a Django session and a Liberty session"""
    django_session_key = models.CharField(max_length = 40)
    session_index = models.CharField(max_length = 80)
    provider_id = models.CharField(max_length = 80)
    federation = models.ForeignKey(LibertyFederation, null = True)
    assertion = models.ForeignKey(LibertyAssertion, null = True)
    name_id_qualifier = models.CharField(max_length = 150,
            verbose_name = _("Qualifier"), null = True)
    name_id_format = models.CharField(max_length = 100,
            verbose_name = _("NameIDFormat"), null = True)
    name_id_content = models.CharField(max_length = 100,
            verbose_name = _("NameID"))
    name_id_sp_name_qualifier = models.CharField(max_length = 100,
            verbose_name = _("SPNameQualifier"), null = True)
    creation = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        saml2_assertion = kwargs.pop('saml2_assertion', None)
        if saml2_assertion:
            kwargs['session_index'] = \
                saml2_assertion.authnStatement[0].sessionIndex
            name_id = saml2_assertion.subject.nameID
            kwargs.update(nameid2kwargs(name_id))
        models.Model.__init__(self, *args, **kwargs)

    def set_nid(self, name_id):
        self.__dict__.update(nameid2kwargs(name_id))

    @classmethod
    def get_for_nameid_and_session_indexes(cls, name_id, session_indexes):
        kwargs = nameid2kwargs(name_id)
        return LibertySession.objects.filter(session_index__in = session_indexes, **kwargs)

    def __unicode__(self):
        return '<LibertySession %s>' % self.__dict__

class LibertySessionSP(models.Model):
    """Store the link between a Django session and a Liberty session on the SP"""
    django_session_key = models.CharField(max_length = 40)
    session_index =  models.CharField(max_length = 80, )
    federation = models.ForeignKey(LibertyFederation)

class KeyValue(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    value = PickledObjectField()

    def __unicode__(self):
        return self.key

def save_key_values(key, *values):
    KeyValue(key = key, value = values).save()

def get_and_delete_key_values(key):
    try:
        kv = KeyValue.objects.get(key=key)
        return kv.value
    except ObjectDoesNotExist:
        return None
