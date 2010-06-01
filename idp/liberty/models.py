from django.db import models
from django.contrib.auth.models import User
import lasso

# Configuration models
def fix_name(name):
    return name.replace(' ', '_').replace('/', '_')

class FilenameGenerator(object):
    def __init__(self, infix):
        self.prefix = infix

    def __call__(self, instance, filename):
        return os.path.join(self.prefix,
                "%s_%s_%s" % (fix_name(instance.name), filename,
                    time.strftime("%Y%m%dT%H:%M:%SZ", time.gmtime())))

class LibertyAttributeMapping(models.Model):
    source_attribute_name = models.CharField(max_length = 40)
    attribute_value_format = models.URLField()
    attribute_name = models.CharField(max_length = 40)

class LibertyAttributeMap(models.Model):
    name = models.CharField(max_length = 40, unique = True)
    mappings = models.ManyToManyField(LibertyAttributeMapping,
            related_name = "maps")

    def __unicode__(self):
        return self.name

class LibertyProvider(models.Model):
    name = models.CharField(max_length = 40, unique = True,
            help_text = "Internal nickname for the service provider")
    entity_id = models.URLField()
    metadata = models.FileField(upload_to = FilenameGenerator("metadata"))
    public_key = models.FileField(upload_to = FilenameGenerator("public_key"))
    ssl_certificate = models.FileField(
            upload_to = FilenameGenerator("ssl_certificate"))

    def __unicode__(self):
        return self.name

class LibertyServiceProvider(LibertyProvider):
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
            related_name = "service_providers")
    # XXX: format in the metadata file, should be suffixed with a start to mark
    # them as special
    default_name_id_format = models.CharField(max_length = 80,
            default = "persistent",
            choices = (("persistent", "Persistent"),
                ("transient", "Transient"),
                ("email", "Email (only supported by SAMLv2)")))


class LibertyIdentityProvider(LibertyProvider):
    want_authn_request_signed = models.BooleanField(
            verbose_name = "Want AuthnRequest signed")
    # Mapping to use to get User attributes from the assertion
    attribute_map = models.ForeignKey(LibertyAttributeMap,
            related_name = "identity_providers")

# Transactional models

class LibertyFederation(models.Model):
    """Store a federation, i.e. an identifier shared with another provider, be
       it IdP or SP"""
    user = models.ForeignKey(User)
    name_id_qualifier = models.CharField(max_length = 150, editable = False,
            verbose_name = "Qualifier")
    name_id_format = models.CharField(max_length = 100, editable = False,
            verbose_name = "NameIDFormat")
    name_id_content = models.CharField(max_length = 100, editable = False,
            verbose_name = "NameID")
    name_id_sp_name_qualifier = models.CharField(max_length = 100, editable = False,
            verbose_name = "SPNameQualifier")

    class Meta:
        verbose_name = "federation"
        verbose_name_plural = "federations"
        # XXX: To allow shared-federation (multiple-user with the same
        # federation), add user to this list
        unique_together = (("name_id_qualifier", "name_id_format",
            "name_id_content", "name_id_sp_name_qualifier"))

class LibertySession(models.Model):
    """Store the link between a Django session and a Liberty session"""
    django_session_key = models.CharField(max_length = 40, editable = False)

# When we receive a logout request, we lookup the LibertyAssertions, then the LibertySession and the the real DjangoSession

class LibertyAssertions(models.Model):
    liberty_session = models.ForeignKey(LibertySession, editable = False,
            related_name = "assertions")
    session_index = models.CharField(max_length = 80, editable = False)
    assertion = models.TextField(editable = False)
    emission_time = models.DateTimeField(auto_now = True, editable = False)

class LibertyArtifact(models.Model):
    """Store an artifact"""
    artifact = models.CharField(max_length = 40, editable = False)
    content = models.TextField(editable = False)
