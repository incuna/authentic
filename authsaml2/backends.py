from django.db import transaction
from django.contrib.auth.models import User, UserManager
import settings
from saml2_endpoints import *
from saml.common import *

class AuthenticationError(Exception):
    pass

class AuthSAML2Backend:

    def authenticate(self, request, login):
        fed = lookup_federation_by_name_identifier(login)
        if fed is None:
            return None
        else:
            fed.user.backend = settings.SAML2_BACKEND
            return fed.user

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @transaction.commit_on_success
    def create_user(self, username=None, nameId=None):
        if not username and not nameId:
            return None
        if not username:
            username = nameId
        try:
            user = User.objects.get(username=username)
            user.backend = settings.SAML2_BACKEND
            user.save()
        except User.DoesNotExist:
            user = self.build_user(username)
        return user

    def build_user(self, username):
        user = User()
        user.username=username
        user.password=UserManager().make_random_password()
        user.is_active = True
        user.backend = settings.SAML2_BACKEND
        user.save()
        return user
