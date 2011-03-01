from django.db import models
from django.contrib.sessions.models import Session
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

class FakePk:
    name = '_pk'

class FakeMeta:
    pk = FakePk()

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
    _pk = -1
    _meta = FakeMeta()

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
        #XXX: Should return True
        return False

    def is_authenticated(self):
        return True

    def get_username(self):
        return _('Anonymous')
    username = property(get_username)
