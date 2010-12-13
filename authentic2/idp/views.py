import urllib

from django.utils.translation import ugettext as _
from django_authopenid.forms import OpenidDissociateForm, AssociateOpenID
from django_authopenid.forms import OpenidSigninForm
from django_authopenid import DjangoOpenIDStore
from django_authopenid.models import UserAssociation
from django_authopenid.utils import *
from django_authopenid.views import associate_failure, complete
from django_authopenid.views import _build_context, signin_success, signin_failure, not_authenticated
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import render_to_response as render
from django.template import RequestContext
from django.utils.encoding import smart_unicode
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic.simple import redirect_to
from openid.consumer.consumer import Consumer, SUCCESS, CANCEL, FAILURE, SETUP_NEEDED
from openid.consumer.discover import DiscoveryFailure
from openid.yadis import xri

import authentic2.saml.common
import authentic2.authsaml2.utils
from authentic2.idp import get_backends

__logout_redirection_timeout = getattr(settings, 'IDP_LOGOUT_TIMEOUT', 600)

def accumulate_from_backends(request, method_name):
    from authentic2.idp import get_backends
    list = []
    for backend in get_backends():
        method = getattr(backend, method_name, None)
        if callable(method):
            list += method(request)
    return list

def service_list(request):
    '''Compute the service list to show on user homepage'''
    return accumulate_from_backends(request, 'service_list')

def homepage(request):
    '''Homepage of the IdP'''
    import authentic2.saml.common
    import authentic2.authsaml2.utils
    tpl_parameters = {}
    tpl_parameters['authorized_services'] = service_list(request)
    if authentic2.authsaml2.utils.is_sp_configured():
        tpl_parameters['provider_active_session'] = authentic2.saml.common.get_provider_of_active_session(request)
        tpl_parameters['provider_name'] = authentic2.saml.common.get_provider_of_active_session_name(request)
    if settings.IDP_OPENID:
        tpl_parameters['openid'] = request.user.openid_set
        tpl_parameters['IDP_OPENID'] = settings.IDP_OPENID
    return render_to_response('idp/homepage.html', tpl_parameters, RequestContext(request))

def profile(request):
    frontends = get_backends('AUTH_FRONTENDS')
    blocks = [ frontend.profile(request, next='/profile') for frontend in frontends \
            if hasattr(frontend, 'profile') ]
    return render_to_response('idp/account_management.html', { 'frontends_block': blocks },
            RequestContext(request))

def logout_list(request):
    '''Return logout links from idp backends'''
    return accumulate_from_backends(request, 'logout_list')

def logout(request, next_page='/', redirect_field_name=REDIRECT_FIELD_NAME,
        template = 'idp/logout.html'):
    global __logout_redirection_timeout
    "Logs out the user and displays 'You are logged out' message."
    do_local = request.REQUEST.has_key('local')
    l = logout_list(request)
    context = RequestContext(request)
    context['redir_timeout'] = __logout_redirection_timeout
    next_page = request.REQUEST.get(redirect_field_name, next_page)
    if l and not do_local:
        # Full logout
        next_page = '?local&next=%s' % urllib.quote(next_page)
        context['logout_list'] = l
        context['next_page'] = next_page
        context['message'] = _('Logging out from all your services')
        return render_to_response(template, context_instance = context)
    else:
        # Local logout
        auth_logout(request)
        context['next_page'] = next_page
        context['message'] = _('Logged out')
        return render_to_response(template, context_instance = context)

def redirect_to_logout(request, next_page='/'):
    return HttpResponseRedirect('%s?next=%s' % (reverse(logout), urllib.quote(next_page)))
