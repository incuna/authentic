from django.db import models
from django.utils.translation import ugettext as _

import lasso

AUTHSAML2_UNAUTH = (
    ('AUTHSAML2_UNAUTH_ACCOUNT_LINKING_BY_AUTH', _('Account linking by authentication')),
#    ('AUTHSAML2_UNAUTH_ACCOUNT_LINKING_BY_ATTRS', _('Account linking by attributes in assertion')),
#    ('AUTHSAML2_UNAUTH_ACCOUNT_LINKING_BY_TOKEN', _('Account linking by a token?')),
#    ('AUTHSAML2_UNAUTH_CREATE_USER_PSEUDONYMOUS_ONE_TIME', _('Create new user only with a certified transient nameID')),
    ('AUTHSAML2_UNAUTH_CREATE_USER_PSEUDONYMOUS', _('Create new user only with a certified persistent nameID')),
#    ('AUTHSAML2_UNAUTH_CREATE_USER_WITH_ATTRS_IN_A8N', _('Create new user with attributes in assertion')),
#    ('AUTHSAML2_UNAUTH_CREATE_USER_WITH_ATTRS_SELF_ASSERTED', _('Create new user with attributes seld-asserted by the user')),
)

AUTHSAML2_BINDING_FOR_AUTHN_REQUEST = (
    (lasso.SAML2_METADATA_BINDING_POST, _('Binding HTTP POST')),
    (lasso.SAML2_METADATA_BINDING_ARTIFACT, _('Binding ARTIFACT')),
#    (lasso.SAML2_METADATA_BINDING_SOAP, _('HTTP SOAP')),
#    (lasso.SAML2_METADATA_BINDING_REDIRECT, _('HTTP REDIRECT')),
)

class MyServiceProvider(models.Model):
    unauth = models.CharField(max_length=80, choices=AUTHSAML2_UNAUTH)
    binding_authn_request = models.CharField(max_length=80, choices=AUTHSAML2_BINDING_FOR_AUTHN_REQUEST)
    back_url = models.CharField(max_length = 80, )

class ExtendDjangoSession(models.Model):
    django_session_key = models.CharField(max_length = 50, unique = True)
    saml_request_id = models.CharField(max_length = 80, )
    federation_in_progress = models.CharField(max_length = 80, )
    next = models.CharField(max_length = 80, )
    temp_identity_dump = models.TextField(blank = True)
