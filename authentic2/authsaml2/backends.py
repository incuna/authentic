import string
import random

from django.db import transaction
from django.contrib.auth.models import User, UserManager
from django.conf import settings
import lasso

from authentic2.saml.common import lookup_federation_by_name_identifier, \
    add_federation
from models import SAML2TransientUser

from authentic2.authsaml2.utils import *

class AuthenticationError(Exception):
    pass

class AuthSAML2PersistentBackend:
    def authenticate(self, name_id=None):
        s = get_service_provider_settings()
        if not s:
            return None

        '''Authenticate persistent NameID'''
        if not name_id or \
             (name_id.format != lasso.SAML2_NAME_IDENTIFIER_FORMAT_PERSISTENT and \
             not s.account_with_transient):# or \
             #not name_id.nameQualifier:
            return None
        fed = lookup_federation_by_name_identifier(name_id=name_id)
        if fed is None:
            return None
        fed.user.backend = 'authentic2.authsaml2.backends.AuthSAML2PersistentBackend'
        return fed.user

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @transaction.commit_on_success
    def create_user(self, username=None, name_id=None):
        '''Create a new user mapping to the given NameID'''
        if not name_id or \
             name_id.format != lasso.SAML2_NAME_IDENTIFIER_FORMAT_PERSISTENT or \
             not name_id.nameQualifier:
            raise ValueError('Invalid NameID')
        if not username:
            # FIXME: maybe keep more information in the forged username
            username = 'saml2-%s' % ''.join([random.choice(string.letters) for x in range(10)])
        user = User()
        user.username=username
        user.password=UserManager().make_random_password()
        user.is_active = True
        user.save()
        add_federation(user, name_id=name_id)
        return user

class AuthSAML2TransientBackend:
    def authenticate(self, name_id=None):
        '''Create temporary user for transient NameID'''
        if not name_id or \
             name_id.format != lasso.SAML2_NAME_IDENTIFIER_FORMAT_TRANSIENT or\
             not name_id.content:
            return None
        user = SAML2TransientUser(id=name_id.content)
        return user

    def get_user(self, user_id):
        '''Create temporary user for transient NameID'''
        return SAML2TransientUser(id=user_id)
