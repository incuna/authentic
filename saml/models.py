from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os.path
import time
import lasso


ATTRIBUTE_VALUE_FORMATS = (
        (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_UNSPECIFIED, 'SAMLv2 unspecified'),
        (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, 'SAMLv2 URI'),
        (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC, 'SAMLv2 Basic'))


def fix_name(name):
    return name.replace(' ', '_').replace('/', '_')

class FilenameGenerator(object):
    def __init__(self, prefix = '', suffix = ''):
        self.prefix = prefix
        self.suffix = suffix

    def __call__(self, instance, filename):
        path = "metadata/%s_%s_%s%s" % (self.prefix,
                    fix_name(instance.entity_id),
                    time.strftime("%Y%m%dT%H:%M:%SZ", time.gmtime()),
                    self.suffix)
        import sys
        print >>sys.stderr, 'path', path
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
    provider=lasso.Provider.newFromBuffer(lasso.PROVIDER_ROLE_NONE, meta)
    if not provider:
        raise ValidationError('Bad metadata file')


class LibertyProvider(models.Model):
    entity_id = models.URLField(unique = True)
    name = models.CharField(max_length = 40, unique = True,
            help_text = "Internal nickname for the service provider")
    protocol_conformance = models.IntegerField(max_length = 10,
            choices = ((0, 'SAML10'),
                       (1, 'SAML11'),
                       (2, 'SAML12'),
                       (3, 'SAML20')))
    metadata = models.FileField(upload_to = FilenameGenerator("metadata", '.xml'),
            validators = [ validate_metadata ])
    public_key = models.FileField(upload_to = FilenameGenerator("public_key", '.pem'),
            blank = True)
    ssl_certificate = models.FileField(
            upload_to = FilenameGenerator("ssl_certificate", '.pem'),
            blank = True)
    ca_cert_chain = models.FileField(
            upload_to = FilenameGenerator('ca_cert_chain', '.pem'),
            blank = True)

    def __unicode__(self):
        return self.name

    def clean(self):
        models.Model.clean(self)
        self.metadata.open()
        meta=self.metadata.read()
        provider=lasso.Provider.newFromBuffer(lasso.PROVIDER_ROLE_NONE, meta)
        if provider:
            self.entity_id = provider.providerId
            self.protocol_conformance = provider.protocolConformance

class LibertyServiceProvider(models.Model):
    liberty_provider = models.OneToOneField(LibertyProvider,
            primary_key = True)
    encrypt_nameid = models.BooleanField(verbose_name = "Encrypt NameID")
    encrypt_assertion = models.BooleanField(
            verbose_name = "Encrypt Assertion")
    authn_request_signed = models.BooleanField(
            verbose_name = "AuthnRequest signed")
    idp_initiated_sso = models.BooleanField(
            verbose_name = "Allow IdP iniated SSO")
    # Mapping to use to produce attributes in the assertions or in Attribute
    # requests
    attribute_map = models.ForeignKey(LibertyAttributeMap,
            related_name = "service_providers",
            blank = True, null = True)
    # XXX: format in the metadata file, should be suffixed with a start to mark
    # them as special
    default_name_id_format = models.CharField(max_length = 80,
            default = "persistent",
            choices = (("persistent", "Persistent"),
                ("transient", "Transient"),
                ("email", "Email (only supported by SAMLv2)")))


class LibertyIdentityProvider(models.Model):
    liberty_provider = models.OneToOneField(LibertyProvider,
            primary_key = True)
    want_authn_request_signed = models.BooleanField(
            verbose_name = "Want AuthnRequest signed")
    # Mapping to use to get User attributes from the assertion
    attribute_map = models.ForeignKey(LibertyAttributeMap,
            related_name = "identity_providers",
            blank = True, null = True)


# Transactional models
class LibertyIdentityDump(models.Model):
    user = models.ForeignKey(User, unique = True)
    identity_dump = models.TextField(blank = True)

class LibertySessionDump(models.Model):
    django_session_key = models.CharField(max_length = 40)
    session_dump = models.TextField(blank = True)

class LibertyArtifact(models.Model):
    """Store an artifact"""
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
            verbose_name = "Qualifier")
    name_id_format = models.CharField(max_length = 100,
            verbose_name = "NameIDFormat")
    name_id_content = models.CharField(max_length = 100,
            verbose_name = "NameID")
    name_id_sp_name_qualifier = models.CharField(max_length = 100,
            verbose_name = "SPNameQualifier")

    class Meta:
        verbose_name = "Liberty federation"
        verbose_name_plural = "Liberty federations"
        # XXX: To allow shared-federation (multiple-user with the same
        # federation), add user to this list
        unique_together = (("name_id_qualifier", "name_id_format",
            "name_id_content", "name_id_sp_name_qualifier"))

