from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.utils.translation import ugettext as _
import os.path
import time
import lasso


# TODO: add other name formats with lasso next release
ATTRIBUTE_VALUE_FORMATS = (
        (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, 'SAMLv2 URI'),)

metadata_store = FileSystemStorage(location=settings.SAML_METADATA_ROOT)

def fix_name(name):
    return name.replace(' ', '_').replace('/', '_')

class FilenameGenerator(object):
    '''Generate a filename to store in media directory'''
    def __init__(self, prefix = '', suffix = ''):
        self.prefix = prefix
        self.suffix = suffix

    def __call__(self, instance, filename):
        path = "%s_%s_%s%s" % (self.prefix,
                    fix_name(instance.entity_id),
                    time.strftime("%Y%m%dT%H:%M:%SZ", time.gmtime()),
                    self.suffix)
        return path

class LibertyAttributeMap(models.Model):
    name = models.CharField(max_length = 40, unique = True)
    def __unicode__(self):
        return self.name

class LibertyAttributeMapping(models.Model):
    source_attribute_name = models.CharField(max_length = 40)
    attribute_value_format = models.URLField(choices = ATTRIBUTE_VALUE_FORMATS)
    attribute_name = models.CharField(max_length = 40)
    map = models.ForeignKey(LibertyAttributeMap)

def validate_metadata(value):
    value.open()
    meta=value.read()
    provider=lasso.Provider.newFromBuffer(lasso.PROVIDER_ROLE_ANY, meta)
    if not provider:
        raise ValidationError(_('Bad metadata file'))

def metadata_field(prefix, suffix, validators = [], blank = True):
    '''Adapt a FileField to the need of metadata saving'''
    return models.FileField(
            upload_to = FilenameGenerator("metadata", '.xml'),
            storage = metadata_store,
            validators = validators, blank = blank)

class LibertyProvider(models.Model):
    entity_id = models.URLField(unique = True)
    name = models.CharField(max_length = 40, unique = True,
            help_text = _("Internal nickname for the service provider"))
    protocol_conformance = models.IntegerField(max_length = 10,
            choices = ((0, 'SAML 1.0'),
                       (1, 'SAML 1.1'),
                       (2, 'SAML 1.2'),
                       (3, 'SAML 2.0')))
    metadata = metadata_field("metadata", '.xml',
            [ validate_metadata ], blank = False)
    public_key = metadata_field("public_key", '.pem')
    ssl_certificate = metadata_field("ssl_certificate", '.pem')
    ca_cert_chain = metadata_field('ca_cert_chain', '.pem')

    def __unicode__(self):
        return self.name

    def clean(self):
        models.Model.clean(self)
        if self.metadata:
            self.metadata.open()
            meta = self.metadata.read()
            provider = lasso.Provider.newFromBuffer(lasso.PROVIDER_ROLE_ANY, meta)
            if provider:
                self.entity_id = provider.providerId
                self.protocol_conformance = provider.protocolConformance

# TODO: Remove this in LibertyServiceProvider
ASSERTION_CONSUMER_PROFILES = (
        ('art', _('Artifact binding')),
        ('post', _('Post binding')))

# TODO: The IdP must look to the preferred binding order for sso in the SP metadata (AssertionConsumerService)
# expect if the protocol for response is defined in the request (ProtocolBinding attribute)
class LibertyServiceProvider(models.Model):
    liberty_provider = models.OneToOneField(LibertyProvider,
            primary_key = True, related_name = 'service_provider')
    enabled = models.BooleanField(verbose_name = _('Enabled'))
    prefered_assertion_consumer_binding = models.CharField(
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
    default_name_id_format = models.CharField(max_length = 80,
            default = "persistent",
            choices = (("persistent", _("Persistent")),
                ("transient", _("Transient")),
                ("email", _("Email (only supported by SAMLv2)"))))
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
# TODO: Add checkbox to enable protocol binding definition for responses.
# - Not checked, not specified in request, the IdP take from the SP metadata
# - Checked, The SP defines in its request the binding for response
class LibertyIdentityProvider(models.Model):
    liberty_provider = models.OneToOneField(LibertyProvider,
            primary_key = True, related_name = 'identity_provider')
    enabled = models.BooleanField(verbose_name = _('Enabled'))
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
            max_length = 100, choices = USER_CONSENT,
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
    creation = models.DateTimeField(auto_now=True)
    artifact = models.CharField(max_length = 40, primary_key = True)
    content = models.TextField()
    django_session_key = models.CharField(max_length = 40)
    provider_id = models.CharField(max_length = 80)

class LibertySession(models.Model):
    """Store the link between a Django session and a Liberty session"""
    django_session_key = models.CharField(max_length = 40)

# When we receive a logout request, we lookup the LibertyAssertions, then the
# LibertySession and the the real DjangoSession
class LibertyAssertions(models.Model):
    assertion_id = models.CharField(max_length = 50, unique = True)
    liberty_session = models.ForeignKey(LibertySession,
            related_name = "assertions")
    session_index = models.CharField(max_length = 80, )
    assertion = models.TextField()
    emission_time = models.DateTimeField(auto_now = True, )

class LibertyFederation(models.Model):
    """Store a federation, i.e. an identifier shared with another provider, be
       it IdP or SP"""
    user = models.ForeignKey(User)
    name_id_qualifier = models.CharField(max_length = 150,
            verbose_name = _("Qualifier"))
    name_id_format = models.CharField(max_length = 100,
            verbose_name = _("NameIDFormat"))
    name_id_content = models.CharField(max_length = 100,
            verbose_name = _("NameID"))
    name_id_sp_name_qualifier = models.CharField(max_length = 100,
            verbose_name = _("SPNameQualifier"))

    class Meta:
        verbose_name = _("Liberty federation")
        verbose_name_plural = _("Liberty federations")
        # XXX: To allow shared-federation (multiple-user with the same
        # federation), add user to this list
        unique_together = (("name_id_qualifier", "name_id_format",
            "name_id_content", "name_id_sp_name_qualifier"))

class LibertySessionSP(models.Model):
    """Store the link between a Django session and a Liberty session on the SP"""
    django_session_key = models.CharField(max_length = 40)
    session_index =  models.CharField(max_length = 80, )
    federation = models.ForeignKey(LibertyFederation)
