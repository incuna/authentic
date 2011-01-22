from django.db import models
from django.utils.translation import ugettext as _
from django.db.models.manager import EmptyManager
import lasso

from authentic2.saml.models import *

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

class AuthorizationAttributeMap(models.Model):
    name = models.CharField(max_length = 40, unique = True)
    def __unicode__(self):
        return self.name

class AttributeMapping(models.Model):
    source_attribute_name = models.CharField(max_length = 40)
    attribute_value_format = models.CharField(max_length = 40)
    attribute_name = models.CharField(max_length = 40)
    attribute_value = models.CharField(max_length = 40)
    map = models.ForeignKey(AuthorizationAttributeMap)

class IdPOptionsPolicy(models.Model):
    name = models.CharField(_('name'), max_length=80, unique=True)
    enabled = models.BooleanField(verbose_name = _('Enabled'))
    no_nameid_policy = models.BooleanField(
            verbose_name = _("Do not send a nameId Policy"))
    requested_name_id_format = models.CharField(max_length = 20,
            default = DEFAULT_NAME_ID_FORMAT,
            choices = NAME_ID_FORMATS_CHOICES)
    transient_is_persistent = models.BooleanField(
            verbose_name = \
            _("This IdP falsely sends a transient NameID \
            which is in fact persistent"))
    allow_create = models.BooleanField(
            verbose_name = _("Allow IdP to create an identity"))
    enable_binding_for_sso_response = models.BooleanField(
            verbose_name = _('Binding for Authnresponse \
            (taken from metadata by the IdP if not enabled)'))
    binding_for_sso_response = models.CharField(
            max_length = 60, choices = BINDING_SSO_IDP,
            verbose_name = '',
            default = lasso.SAML2_METADATA_BINDING_ARTIFACT)
    enable_http_method_for_slo_request = models.BooleanField(
            verbose_name = _('HTTP method for single logout request \
            (taken from metadata if not enabled)'))
    http_method_for_slo_request = models.IntegerField(
            max_length = 60, choices = HTTP_METHOD,
            verbose_name = '',
            default = lasso.HTTP_METHOD_REDIRECT)
    enable_http_method_for_defederation_request = models.BooleanField(
            verbose_name = \
            _('HTTP method for federation termination request \
            (taken from metadata if not enabled)'))
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
    attribute_map = models.ForeignKey(AuthorizationAttributeMap,
            related_name = "authorization_attributes",
            blank = True, null = True)

    class Meta:
        verbose_name = _('identity provider options policy')
        verbose_name_plural = _('identity provider options policies')

    def __unicode__(self):
        return self.name

'''
class idPGroup(models.Model):
    name = models.CharField(_('name'), max_length=80, unique=True)
    policy = models.ForeignKey(IdPOptionsPolicy)

    class Meta:
        verbose_name = _('identity providers group')
        verbose_name_plural = _('identity providers groups')

    def __unicode__(self):
        return self.name
'''

# TODO: remove options after handling
class MyServiceProvider(models.Model):
    handle_persistent = models.CharField(
            max_length=80,
            verbose_name = 'Account Policy with persistent nameId',
            choices=AUTHSAML2_UNAUTH_PERSISTENT)
    handle_transient = models.CharField(
            max_length=80,
            verbose_name = 'Access Policy with transient nameId',
            choices=AUTHSAML2_UNAUTH_TRANSIENT)
    back_url = models.CharField(
            max_length = 80,
            verbose_name = 'Return URL after a successful authentication')

    class Meta:
        verbose_name = _('Service provider core configuration')

    def __unicode__(self):
        return "Service provider core configuration"

class ExtendDjangoSession(models.Model):
    django_session_key = models.CharField(max_length = 50, unique = True)
    saml_request_id = models.CharField(max_length = 80, )
    federation_in_progress = models.CharField(max_length = 80, )
    next = models.CharField(max_length = 80, )
    temp_identity_dump = models.TextField(blank = True)

class SAML2TransientUser(object):
    '''Class compatible with django.contrib.auth.models.User
       which represent an user authenticated using a Transient
       federation'''
    id = None
    is_staff = False
    is_active = False
    is_superuser = False
    _groups = EmptyManager()
    _user_permissions = EmptyManager()

    def __init__(self, id):
        self.id = id

    def __unicode__(self):
        return 'AnonymousUser'

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 1 # instances always return the same hash value

    def save(self):
        pass

    def delete(self):
        raise NotImplementedError

    def set_password(self, raw_password):
        raise NotImplementedError

    def check_password(self, raw_password):
        raise NotImplementedError

    def _get_groups(self):
        return self._groups
    groups = property(_get_groups)

    def _get_user_permissions(self):
        return self._user_permissions
    user_permissions = property(_get_user_permissions)

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj=obj)

    def has_perm(self, perm, obj=None):
        return _user_has_perm(self, perm, obj=obj)

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def has_module_perms(self, module):
        return _user_has_module_perms(self, module)

    def get_and_delete_messages(self):
        return []

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_username(self):
        return _('Anonymous')
    username = property(get_username)
