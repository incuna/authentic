import string
import random

from django.db import transaction
from django.contrib.auth.models import User, UserManager
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
import lasso

from authentic2.saml.common import \
    lookup_federation_by_name_id_and_provider_id, add_federation
from authentic2.saml.models import LIBERTY_SESSION_DUMP_KIND_SP, \
    LibertySessionDump, LibertyProvider
from authentic2.authsaml2.models import SAML2TransientUser

class AuthenticationError(Exception):
    pass

class AuthSAML2Backend:
    def logout_list(self, request):
        pid = None
        q = LibertySessionDump. \
            objects.filter(django_session_key=request.session.session_key,
                    kind=LIBERTY_SESSION_DUMP_KIND_SP)
        if not q:
            return []
        try:
            pid = lasso.Session().newFromDump(q[0].session_dump). \
                get_assertions().keys()[0]
        except:
            pass
        if not pid:
            return []
        name = pid
        try:
            name = LibertyProvider.objects.get(entity_id=pid).name
        except LibertyProvider.DoesNotExist:
            pass
        import saml2_endpoints
        code = '<div>'
        code += _('Sending logout to %(pid)s....') % { 'pid': name or pid }
        code += '<iframe src="%s" marginwidth="0" marginheight="0" \
scrolling="no" style="border: none" width="16" height="16"></iframe></div>' % \
                reverse(saml2_endpoints.sp_slo, args=[pid])
        return [ code ]

class AuthSAML2PersistentBackend:
    supports_object_permissions = False
    supports_anonymous_user = False

    def authenticate(self, name_id=None, provider_id=None):
        '''Authenticate persistent NameID'''
        if not name_id or not provider_id:# or not name_id.nameQualifier:
            return None
        #fed = lookup_federation_by_name_identifier(name_id=name_id)
        fed = lookup_federation_by_name_id_and_provider_id(name_id, provider_id)
        if fed is None:
            return None
        fed.user.backend = '%s.%s' % (__name__, self.__class__.__name__)
        return fed.user

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @transaction.commit_on_success
    def create_user(self, username=None, name_id=None, provider_id=None):
        '''Create a new user mapping to the given NameID'''
        if not name_id or \
                 name_id.format != \
                 lasso.SAML2_NAME_IDENTIFIER_FORMAT_PERSISTENT or \
                 not name_id.nameQualifier:
            raise ValueError('Invalid NameID')
        if not username:
            # FIXME: maybe keep more information in the forged username
            username = 'saml2-%s' % ''. \
                join([random.choice(string.letters) for x in range(10)])
        user = User()
        user.username=username
        user.password=UserManager().make_random_password()
        user.is_active = True
        user.save()
        add_federation(user, name_id=name_id, provider_id=provider_id)
        return user

class AuthSAML2TransientBackend:
    supports_object_permissions = False
    supports_anonymous_user = False

    def authenticate(self, name_id=None):
        '''Create temporary user for transient NameID'''
        if not name_id or \
                name_id.format != \
                lasso.SAML2_NAME_IDENTIFIER_FORMAT_TRANSIENT or \
                not name_id.content:
            return None
        user = SAML2TransientUser(id=name_id.content)
        return user

    def get_user(self, user_id):
        '''Create temporary user for transient NameID'''
        return SAML2TransientUser(id=user_id)
