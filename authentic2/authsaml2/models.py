from django.db import models
from django.utils.translation import ugettext as _
from authentic2.saml.models import *
import lasso

AUTHSAML2_UNAUTH_PERSISTENT = (
    ('AUTHSAML2_UNAUTH_PERSISTENT_ACCOUNT_LINKING_BY_AUTH', _('Account linking by authentication')),
    ('AUTHSAML2_UNAUTH_PERSISTENT_CREATE_USER_PSEUDONYMOUS', _('Create new account')),
)

AUTHSAML2_UNAUTH_TRANSIENT = (
    ('AUTHSAML2_UNAUTH_TRANSIENT_ASK_AUTH', _('Ask authentication')),
    ('AUTHSAML2_UNAUTH_TRANSIENT_OPEN_SESSION', _('Open a session')),
)

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
    activate_default_sp_policy = models.BooleanField(
            verbose_name = _("Activate the following policy for all SAML2 IdP:"))
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
    #attribute_map = models.ForeignKey(LibertyAttributeMap,
    #        related_name = "identity_providers",
    #        blank = True, null = True)


class ExtendDjangoSession(models.Model):
    django_session_key = models.CharField(max_length = 50, unique = True)
    saml_request_id = models.CharField(max_length = 80, )
    federation_in_progress = models.CharField(max_length = 80, )
    next = models.CharField(max_length = 80, )
    temp_identity_dump = models.TextField(blank = True)
