import xml.etree.ElementTree as etree
import hashlib
import binascii
import base64
import datetime

import lasso
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.utils.importlib import import_module

from fields import PickledObjectField, MultiSelectField

from authentic2.idp.models import AttributePolicy


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
    best_score = -1
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


SIGNATURE_VERIFY_HINT = {
        lasso.PROFILE_SIGNATURE_VERIFY_HINT_MAYBE: _('Let authentic decides which signatures to check'),
        lasso.PROFILE_SIGNATURE_VERIFY_HINT_FORCE: _('Always check signatures'),
        lasso.PROFILE_SIGNATURE_VERIFY_HINT_IGNORE: _('Does not check signatures') }


class LibertyProviderPolicy(models.Model):
    name = models.CharField(max_length=64, unique=True)
    authn_request_signature_check_hint = models.IntegerField(
            verbose_name=_("How to verify signatures Authentication Request ?"),
            choices=SIGNATURE_VERIFY_HINT.items(),
            default=lasso.PROFILE_SIGNATURE_VERIFY_HINT_MAYBE)
    def __unicode__(self):
        options = []
        options.append('AuthnRequest signature: ' + SIGNATURE_VERIFY_HINT[self.authn_request_signature_check_hint])
        return self.name + ' (%s)' % ', '.join(options)


AUTHSAML2_UNAUTH_PERSISTENT = (
    ('AUTHSAML2_UNAUTH_PERSISTENT_ACCOUNT_LINKING_BY_AUTH',
        _('Account linking by authentication')),
    ('AUTHSAML2_UNAUTH_PERSISTENT_CREATE_USER_PSEUDONYMOUS',
        _('Create new account')),
)

AUTHSAML2_UNAUTH_TRANSIENT = (
    ('AUTHSAML2_UNAUTH_TRANSIENT_ASK_AUTH', _('Ask authentication')),
    ('AUTHSAML2_UNAUTH_TRANSIENT_OPEN_SESSION', _('Open a session')),
)


class IdPOptionsSPPolicy(models.Model):
    '''
        Policies configured as a SAML2 service provider.

        Used to define SAML2 parameters employed with third SAML2 identity
        providers
    '''
    name = models.CharField(_('name'), max_length=200, unique=True)
    enabled = models.BooleanField(verbose_name = _('Enabled'))
    no_nameid_policy = models.BooleanField(
            verbose_name = _("Do not send a nameId Policy"))
    requested_name_id_format = models.CharField(
            verbose_name = _("Requested NameID format"),
            max_length = 200,
            default = DEFAULT_NAME_ID_FORMAT,
            choices = NAME_ID_FORMATS_CHOICES)
    transient_is_persistent = models.BooleanField(
            verbose_name = \
_("This IdP falsely sends a transient NameID which is in fact persistent"))
    allow_create = models.BooleanField(
            verbose_name = _("Allow IdP to create an identity"))
    enable_binding_for_sso_response = models.BooleanField(
            verbose_name = _('Binding for Authnresponse \
            (taken from metadata by the IdP if not enabled)'))
    binding_for_sso_response = models.CharField(
            verbose_name = _("Binding for the SSO responses"),
            max_length = 200, choices = BINDING_SSO_IDP,
            default = lasso.SAML2_METADATA_BINDING_ARTIFACT)
    enable_http_method_for_slo_request = models.BooleanField(
            verbose_name = _('HTTP method for single logout request \
            (taken from metadata if not enabled)'))
    http_method_for_slo_request = models.IntegerField(
            verbose_name = _("HTTP binding for the SLO requests"),
            max_length = 200, choices = HTTP_METHOD,
            default = lasso.HTTP_METHOD_REDIRECT)
    enable_http_method_for_defederation_request = models.BooleanField(
            verbose_name = \
            _('HTTP method for federation termination request \
            (taken from metadata if not enabled)'))
    http_method_for_defederation_request = models.IntegerField(
            verbose_name = _("HTTP method for the SLO requests"),
            max_length = 200, choices = HTTP_METHOD,
            default = lasso.HTTP_METHOD_SOAP)
    force_user_consent = models.BooleanField(\
            verbose_name = \
                _("Require the user consent be given at account linking"),
            default=False)
    want_force_authn_request = models.BooleanField(
            verbose_name = _("Force authentication"))
    want_is_passive_authn_request = models.BooleanField(
            verbose_name = _("Passive authentication"))
    want_authn_request_signed = models.BooleanField(
            verbose_name = _("Want AuthnRequest signed"))
    handle_persistent = models.CharField(
            max_length=200,
            verbose_name = _('Behavior with persistent NameID'),
            choices=AUTHSAML2_UNAUTH_PERSISTENT,
            default = 'AUTHSAML2_UNAUTH_PERSISTENT_ACCOUNT_LINKING_BY_AUTH')
    handle_transient = models.CharField(
            max_length=200,
            verbose_name = _('Behavior with transient NameID'),
            choices=AUTHSAML2_UNAUTH_TRANSIENT,
            default = '')
    back_url = models.CharField(
            max_length = 200,
            default = '/',
            verbose_name = _('Return URL after a successful authentication'))
    accept_slo = models.BooleanField(\
            verbose_name = _("Accept to receive Single Logout requests"),
            default=True)
    forward_slo = models.BooleanField(\
            verbose_name = _("Forward Single Logout requests"),
            default=True)

    class Meta:
        verbose_name = _('identity provider options policy')
        verbose_name_plural = _('identity provider options policies')

    def __unicode__(self):
        return self.name


class SPOptionsIdPPolicy(models.Model):
    '''
        Policies configured as a SAML2 identity provider.

        Used to define SAML2 parameters employed with service providers.
    '''
    name = models.CharField(_('name'), max_length=80, unique=True)
    enabled = models.BooleanField(verbose_name = _('Enabled'))
    prefered_assertion_consumer_binding = models.CharField(
            verbose_name = _("Prefered assertion consumer binding"),
            default = 'meta',
            max_length = 4, choices = ASSERTION_CONSUMER_PROFILES)
    encrypt_nameid = models.BooleanField(verbose_name = _("Encrypt NameID"))
    encrypt_assertion = models.BooleanField(
            verbose_name = _("Encrypt Assertion"))
    authn_request_signed = models.BooleanField(
            verbose_name = _("Authentication request signed"))
    idp_initiated_sso = models.BooleanField(
            verbose_name = _("Allow IdP initiated SSO"))
    # XXX: format in the metadata file, should be suffixed with a star to mark
    # them as special
    default_name_id_format = models.CharField(max_length = 200,
            default = DEFAULT_NAME_ID_FORMAT,
            choices = NAME_ID_FORMATS_CHOICES)
    accepted_name_id_format = MultiSelectField(
            verbose_name = _("NameID formats accepted"),
            max_length=ACCEPTED_NAME_ID_FORMAT_LENGTH,
            blank=True, choices=NAME_ID_FORMATS_CHOICES)
    # TODO: add clean method which checks that the LassoProvider we can create
    # with the metadata file support the SP role
    # i.e. provider.roles & lasso.PROVIDER_ROLE_SP != 0
    ask_user_consent = models.BooleanField(
        verbose_name = _('Ask user for consent when creating a federation'), default = False)
    accept_slo = models.BooleanField(\
            verbose_name = _("Accept to receive Single Logout requests"),
            default=True)
    forward_slo = models.BooleanField(\
            verbose_name = _("Forward Single Logout requests"),
            default=True)

    class Meta:
        verbose_name = _('service provider options policy')
        verbose_name_plural = _('service provider options policies')

    def __unicode__(self):
        return self.name


class AuthorizationAttributeMap(models.Model):
    name = models.CharField(max_length = 40, unique = True)
    def __unicode__(self):
        return self.name

class AuthorizationAttributeMapping(models.Model):
    source_attribute_name = models.CharField(max_length = 40,
            blank=True)
    attribute_value_format = models.CharField(max_length = 40,
            blank=True)
    attribute_name = models.CharField(max_length = 40)
    attribute_value = models.CharField(max_length = 40)
    map = models.ForeignKey(AuthorizationAttributeMap)

class AuthorizationSPPolicy(models.Model):
    name = models.CharField(_('name'), max_length=80, unique=True)
    enabled = models.BooleanField(verbose_name = _('Enabled'))
    attribute_map = models.ForeignKey(AuthorizationAttributeMap,
            related_name = "authorization_attributes",
            blank = True, null = True)
    default_denial_message = models.CharField(
            max_length = 80,
            verbose_name = \
            _("Default message to display to the user when access is denied"),
            default=_('You are not authorized to access the service.'))

    class Meta:
        verbose_name = _('authorization policy')
        verbose_name_plural = _('authorization policies')

    def __unicode__(self):
        return self.name

class LibertyProvider(models.Model):
    entity_id = models.URLField(unique = True)
    entity_id_sha1 = models.CharField(max_length = 40, blank=True)
    name = models.CharField(max_length = 140,
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
    federation_source = models.CharField(max_length=64, blank=True, null=True)

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
        p = lasso.Provider.newFromBuffer(lasso.PROVIDER_ROLE_ANY, self.metadata.encode('utf8'))
        self.entity_id = p.providerId
        if not self.name:
            self.name = organization_name(p)
        if not self.protocol_conformance:
            self.protocol_conformance = p.protocolConformance

# TODO: The IdP must look to the preferred binding order for sso in the SP metadata (AssertionConsumerService)
# expect if the protocol for response is defined in the request (ProtocolBinding attribute)
class LibertyServiceProvider(models.Model):
    liberty_provider = models.OneToOneField(LibertyProvider,
            primary_key = True, related_name = 'service_provider')
    enabled = models.BooleanField(verbose_name = _('Enabled'))
    enable_following_sp_options_policy = models.BooleanField(verbose_name = \
        _('The following options policy will apply except if a policy for all service provider is defined.'))
    sp_options_policy = models.ForeignKey(SPOptionsIdPPolicy, related_name = "sp_options_policy", verbose_name = _('SP Options Policy'), blank=True, null=True)
    policy = models.ForeignKey(LibertyProviderPolicy,
            verbose_name=_("Protocol policy"), null=True, default=1)
    enable_following_attribute_policy = models.BooleanField(verbose_name = \
        _('The following attribute policy will apply except if a policy for all service provider is defined.'))
    attribute_policy = models.ForeignKey(AttributePolicy,
             related_name = "attribute_policy",
            verbose_name=_("Attribute policy"), null=True, blank=True)


# TODO: The choice for requests must be restricted by the IdP metadata
# The SP then chooses the binding in this list.
# For response, if the requester uses a (a)synchronous binding, the responder uses the same.
# However, the responder can choose which asynchronous binding it employs.
class LibertyIdentityProvider(models.Model):
    liberty_provider = models.OneToOneField(LibertyProvider,
            primary_key = True, related_name = 'identity_provider')
    enabled = models.BooleanField(verbose_name = _('Enabled'))
    enable_following_idp_options_policy = models.BooleanField(verbose_name = \
        _('The following options policy will apply except if a policy for all identity provider is defined.'))
    idp_options_policy = models.ForeignKey(IdPOptionsSPPolicy, related_name = "idp_options_policy", verbose_name = _('IdP Options Policy'), blank=True, null=True)
    enable_following_authorization_policy = models.BooleanField(verbose_name = \
        _('The following authorization policy will apply except if a policy for all identity provider is defined.'))
    authorization_policy = models.ForeignKey(AuthorizationSPPolicy, related_name = "authorization_policy", verbose_name = _('Authorization Policy'), blank=True, null=True)

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

class SessionLinkedManager(models.Manager):
    def cleanup(self):
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        for o in self.all():
            key = o.django_session_key
            if not store.exists(key):
                o.delete()
            else:
                session = engine.SessionStore(session_key=key)
                if session.get_expiry_date() >= datetime.datetime.now():
                    store.delete(key)
                    o.delete()

LIBERTY_SESSION_DUMP_KIND_SP = 0
LIBERTY_SESSION_DUMP_KIND_IDP = 1
LIBERTY_SESSION_DUMP_KIND = { LIBERTY_SESSION_DUMP_KIND_SP: 'sp',
        LIBERTY_SESSION_DUMP_KIND_IDP: 'idp' }

class LibertySessionDump(models.Model):
    '''Store lasso session object dump.

       Should be replaced in the future by direct references to known
       assertions through the LibertySession object'''
    django_session_key = models.CharField(max_length = 40)
    session_dump = models.TextField(blank = True)
    kind = models.IntegerField(choices = LIBERTY_SESSION_DUMP_KIND.items())

    objects = SessionLinkedManager()

class LibertyManageDump(models.Model):
    '''Store lasso manage dump

       Should be replaced in the future by direct reference to ?
       objects'''
    django_session_key = models.CharField(max_length = 40)
    manage_dump = models.TextField(blank = True)

    objects = SessionLinkedManager()

class LibertyArtifactManager(models.Manager):
    def cleanup(self):
        # keep artifacts 10 minutes
        expire = getattr(settings, 'SAML2_ARTIFACT_EXPIRATION', 600)
        before = datetime.datetime.now()-datetime.timedelta(seconds=expire)
        self.filter(creation__lt=before).delete()

class LibertyArtifact(models.Model):
    """Store an artifact and the associated XML content"""
    creation = models.DateTimeField(auto_now_add=True)
    artifact = models.CharField(max_length = 40, primary_key = True)
    content = models.TextField()
    django_session_key = models.CharField(max_length = 40)
    provider_id = models.CharField(max_length = 80)

    objects = LibertyArtifactManager()

def nameid2kwargs(name_id):
    return { 'name_id_qualifier': name_id.nameQualifier,
        'name_id_sp_name_qualifier': name_id.spNameQualifier,
        'name_id_content': name_id.content,
        'name_id_format': name_id.format }

class LibertyAssertionManager(models.Manager):
    def cleanup(self):
        # keep assertions 1 week
        expire = getattr(settings, 'SAML2_ASSERTION_EXPIRATION', 3600*24*7)
        before = datetime.datetime.now()-datetime.timedelta(seconds=expire)
        self.filter(creation__lt=before).delete()

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

    def __unicode__(self):
        return '<LibertyFederation %s>' % self.__dict__


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

    objects = SessionLinkedManager()

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
