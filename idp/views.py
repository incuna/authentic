from django.contrib.auth.views  import logout
from django.contrib.auth import REDIRECT_FIELD_NAME
from signals import auth_logout

import authentic.saml.common
import authentic.authsaml2.utils

def authsaml2_login_page(request):
    if not authentic.authsaml2.utils.is_sp_configured():
        return {}
    return {'providers_list': authentic.saml.common.get_idp_list()}

def AuthLogout(request, next_page=None, redirect_field_name=REDIRECT_FIELD_NAME):
    auth_logout.send(sender = None, user = request.user)
    return logout(request, template_name = 'registration/logout.html', next_page = next_page, redirect_field_name=redirect_field_name)
# Create your views here.
