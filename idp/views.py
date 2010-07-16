from django.contrib.auth.views  import logout
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response as render
from django.http import HttpResponseRedirect
from django.utils.encoding import smart_unicode
from django.conf import settings
from signals import auth_logout
from signals import auth_oidlogin

from django_authopenid import DjangoOpenIDStore
from django_authopenid.forms import OpenidSigninForm
from django_authopenid.views import _build_context, signin_success, signin_failure, not_authenticated
from django_authopenid.utils import *
from openid.yadis import xri
from openid.consumer.discover import DiscoveryFailure
from openid.consumer.consumer import Consumer, \
    SUCCESS, CANCEL, FAILURE, SETUP_NEEDED
from django.views.decorators.csrf import csrf_exempt

import urllib

import authentic.saml.common
import authentic.authsaml2.utils

def authsaml2_login_page(request):
    if not authentic.authsaml2.utils.is_sp_configured():
        return {}
    return {'providers_list': authentic.saml.common.get_idp_list()}

def AuthLogout(request, next_page=None, redirect_field_name=REDIRECT_FIELD_NAME):
    auth_logout.send(sender = None, user = request.user)
    return logout(request, template_name = 'registration/logout.html', next_page = next_page, redirect_field_name=redirect_field_name)


@csrf_exempt
def mycomplete(request, on_success=None, on_failure=None, return_to=None, 
    **kwargs):
    on_success = on_success or default_on_success
    on_failure = on_failure or default_on_failure
    consumer = Consumer(request.session, DjangoOpenIDStore())
    # make sure params are encoded in utf8
    params = dict((k,smart_unicode(v)) for k, v in request.GET.items())
    openid_response = consumer.complete(params, return_to)
    if openid_response.status == SUCCESS:
        auth_oidlogin.send(sender = None, openid_url = request.GET['openid.identity'], state = 'success')
        return on_success(request, openid_response.identity_url,
                openid_response, **kwargs)
    elif openid_response.status == CANCEL:
        auth_oidlogin.send(sender = None, openid_url = request.GET['openid.identity'], state = 'cancel')
        return on_failure(request, 'The request was canceled', **kwargs)
    elif openid_response.status == FAILURE:
        auth_oidlogin.send(sender = None, openid_url = request.GET['openid.identity'], state = 'failure')
        return on_failure(request, openid_response.message, **kwargs)
    elif openid_response.status == SETUP_NEEDED:
        auth_oidlogin.send(sender = None, openid_url = request.GET['openid.identity'], state = 'setup_needed')
        return on_failure(request, 'Setup needed', **kwargs)
    else:
        assert False, "Bad openid status: %s" % openid_response.status

@csrf_exempt
def complete_signin(request, redirect_field_name=REDIRECT_FIELD_NAME,  
        openid_form=OpenidSigninForm, auth_form=AuthenticationForm, 
        on_success=signin_success, on_failure=signin_failure, 
        extra_context=None):
    
    return mycomplete(request, on_success, on_failure,
            get_url_host(request) + reverse('user_complete_signin'),
            redirect_field_name=redirect_field_name, openid_form=openid_form, 
            auth_form=auth_form, extra_context=extra_context)

def ask_openid(request, openid_url, redirect_to, on_failure=None):
    on_failure = on_failure or signin_failure
    sreg_req = None
    ax_req = None
    _openid_url = openid_url
    
    trust_root = getattr(
        settings, 'OPENID_TRUST_ROOT', get_url_host(request) + '/'
    )
    if xri.identifierScheme(openid_url) == 'XRI' and getattr(
            settings, 'OPENID_DISALLOW_INAMES', False
    ):
        msg = ("i-names are not supported")
        auth_oidlogin.send(sender = None, openid_url = _openid_url, state = 'not_supported')
        return on_failure(request, msg)
    consumer = Consumer(request.session, DjangoOpenIDStore())
    try:
        auth_request = consumer.begin(openid_url)
    except DiscoveryFailure:
        msg = ("The OpenID %s was invalid") % openid_url
        auth_oidlogin.send(sender = None, openid_url = _openid_url, state = 'invalid')
        return on_failure(request, msg)
    
    # get capabilities
    use_ax, use_sreg = discover_extensions(openid_url)
    if use_sreg:
        # set sreg extension
        # we always ask for nickname and email
        sreg_attrs = getattr(settings, 'OPENID_SREG', {})
        sreg_attrs.update({ "optional": ['nickname', 'email'] })
        sreg_req = sreg.SRegRequest(**sreg_attrs)
    if use_ax:
        # set ax extension
        # we always ask for nickname and email
        ax_req = ax.FetchRequest()
        ax_req.add(ax.AttrInfo('http://schema.openid.net/contact/email', 
                                alias='email', required=True))
        ax_req.add(ax.AttrInfo('http://schema.openid.net/namePerson/friendly', 
                                alias='nickname', required=True))
                      
        # add custom ax attrs          
        ax_attrs = getattr(settings, 'OPENID_AX', [])
        for attr in ax_attrs:
            if len(attr) == 2:
                ax_req.add(ax.AttrInfo(attr[0], required=alias[1]))
            else:
                ax_req.add(ax.AttrInfo(attr[0]))
       
    if sreg_req is not None:
        auth_request.addExtension(sreg_req)
    if ax_req is not None:
        auth_request.addExtension(ax_req)
    
    redirect_url = auth_request.redirectURL(trust_root, redirect_to)
    return HttpResponseRedirect(redirect_url)

@csrf_exempt
@not_authenticated
def signin(request, template_name='authopenid/signin.html', 
        redirect_field_name=REDIRECT_FIELD_NAME, openid_form=OpenidSigninForm,
        auth_form=AuthenticationForm, on_failure=None, extra_context=None):
    
    if on_failure is None:
        on_failure = signin_failure
        
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    form1 = openid_form()
    form2 = auth_form()
    if request.POST:
        if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL     
        if 'openid_url' in request.POST.keys():
            form1 = openid_form(data=request.POST)
            if form1.is_valid():
                redirect_url = "%s%s?%s" % (
                        get_url_host(request),
                        reverse('user_complete_signin'), 
                        urllib.urlencode({ redirect_field_name: redirect_to })
                )
                return ask_openid(request, 
                        form1.cleaned_data['openid_url'], 
                        redirect_url, 
                        on_failure=on_failure)
        else:
            # perform normal django authentification
            form2 = auth_form(data=request.POST)
            if form2.is_valid():
                login(request, form2.get_user())
                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()
                return HttpResponseRedirect(redirect_to)
    return render(template_name, {
        'form1': form1,
        'form2': form2,
        redirect_field_name: redirect_to,
        'msg':  request.GET.get('msg','')
    }, context_instance=_build_context(request, extra_context=extra_context))


# Create your views here.
