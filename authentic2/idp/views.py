import urllib

from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import SiteProfileNotAvailable
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist

from authentic2.idp import get_backends
from authentic2.authsaml2.models import SAML2TransientUser

__logout_redirection_timeout = getattr(settings, 'IDP_LOGOUT_TIMEOUT', 600)

def accumulate_from_backends(request, method_name):
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
    tpl_parameters = {}
    type(SAML2TransientUser)
    if not isinstance(request.user, SAML2TransientUser):
        tpl_parameters['account_management'] = 'account_management'
        tpl_parameters['authorized_services'] = service_list(request)
    return render_to_response('idp/homepage.html',
       tpl_parameters, RequestContext(request))

def profile(request):

    frontends = get_backends('AUTH_FRONTENDS')

    if request.method == "POST":
        for frontend in frontends:
            if not frontend.enabled():
                continue
            if 'submit-%s' % frontend.id() in request.POST:
                form = frontend.form()(data=request.POST)
                if form.is_valid():
                    if request.session.test_cookie_worked():
                        request.session.delete_test_cookie()
                    return frontend.post(request, form, None, '/profile')
    # User attributes management
    try:
        user_profile = request.user.get_profile()
        profile = []
        for field_name in user_profile._meta.get_all_field_names():
            if field_name in ('id', 'user'):
                continue
            field = user_profile._meta.get_field_by_name(field_name)[0]
            value = getattr(user_profile, field_name)
            if value:
                profile.append((field.verbose_name, value))
    except (SiteProfileNotAvailable, ObjectDoesNotExist):
        profile = ()
    # Credentials management
    blocks = [ frontend.profile(request, next='/profile') for frontend in frontends \
            if hasattr(frontend, 'profile') ]
    return render_to_response('idp/account_management.html', { 'frontends_block': blocks, 'profile': profile },
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
