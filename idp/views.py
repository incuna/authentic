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
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.template import RequestContext
from django.shortcuts import render_to_response
import urllib

import authentic.saml.common
import authentic.authsaml2.utils

from django_authopenid.forms import OpenidDissociateForm, AssociateOpenID
from django_authopenid.models import UserAssociation
from django_authopenid.views import associate_failure, complete
from django.views.generic.simple import redirect_to

OPENID_PROVIDER = ['https://me.yahoo.com//','http://openid.aol.com/','http://.myopenid.com/',
                    'http://.livejournal.com/','http://www.flickr.com/photos//','http://.wordpress.com/'
                    'http://.blogspot.com/','http://.pip.verisignlabs.com/','http://.myvidoop.com/'
                    'http://.pip.verisignlabs.com/','http://claimid.com/']

def authsaml2_login_page(request):
    if not authentic.authsaml2.utils.is_sp_configured():
        return {}
    return {'providers_list': authentic.saml.common.get_idp_list()}

def AuthLogout(request, next_page='/', redirect_field_name=REDIRECT_FIELD_NAME):
    "Logs out the user and displays 'You are logged out' message."

    auth_logout.send(sender = None, user = request.user)
    from django.contrib.auth import logout
    logout(request)

    if next_page is None or next_page == '/':
        redirect_to = request.REQUEST.get(redirect_field_name, '')
        if len(redirect_to) != 0:
            return HttpResponseRedirect(redirect_to)
        else:
            return HttpResponseRedirect(next_page or request.path)
    else:
        return HttpResponseRedirect(next_page or request.path)


@csrf_exempt
def mycomplete(request, on_success=None, on_failure=None, return_to=None, 
    **kwargs):
    on_success = on_success or default_on_success
    on_failure = on_failure or default_on_failure
    consumer = Consumer(request.session, DjangoOpenIDStore())
    # make sure params are encoded in utf8
    params = dict((k,smart_unicode(v)) for k, v in request.GET.items())
    openid_response = consumer.complete(params, return_to)

    if not hasattr(request.GET,'openid.identity'):
        _openid_url = 'None'
    else:
        _openid_url = request.GET['openid.identity']

    if openid_response.status == SUCCESS:
        auth_oidlogin.send(sender = None, openid_url = _openid_url, state = 'success')
        return on_success(request, openid_response.identity_url,
                openid_response, **kwargs)
    elif openid_response.status == CANCEL:
        auth_oidlogin.send(sender = None, openid_url = _openid_url, state = 'cancel')
        return on_failure(request, 'The request was canceled', **kwargs)
    elif openid_response.status == FAILURE:
        auth_oidlogin.send(sender = None, openid_url = _openid_url, state = 'failure')
        return on_failure(request, openid_response.message, **kwargs)
    elif openid_response.status == SETUP_NEEDED:
        auth_oidlogin.send(sender = None, openid_url = _openid_url, state = 'setup_needed')
        return on_failure(request, 'Setup needed', **kwargs)
    else:
        assert False, "Bad openid status: %s" % openid_response.status

@csrf_exempt
def complete_signin(request, redirect_field_name=REDIRECT_FIELD_NAME,  
        openid_form=OpenidSigninForm, auth_form=AuthenticationForm, 
        on_success=signin_success, on_failure=signin_failure, 
        extra_context=None):
    
    _openid_form = openid_form
    _auth_form = auth_form
    _extra_context = extra_context
    
    return mycomplete(request, on_success, on_failure,
            get_url_host(request) + reverse('user_complete_signin'),
            redirect_field_name=redirect_field_name, openid_form=_openid_form, 
            auth_form=_auth_form, extra_context=_extra_context)

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

@csrf_protect
@login_required
def password_change(request, template = 'authopenid/password_change_form.html',
        post_change_redirect = None, password_change_form  = PasswordChangeForm):
    if post_change_redirect is None:
        post_change_redirect = reverse('django.contrib.auth.views.password_change_done')
    if request.method == 'POST':
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    
    if request.user.password == '!':
        context = RequestContext(request)
        context['set_password'] = True 
    else:
        context = RequestContext(request)
    
    return render_to_response(template, {
        'form': form,
    }, context_instance=context)

@csrf_exempt
@login_required
def dissociate(request, template_name="authopenid/dissociate.html",
        dissociate_form=OpenidDissociateForm, 
        redirect_field_name=REDIRECT_FIELD_NAME, 
        default_redirect=settings.LOGIN_REDIRECT_URL, extra_context=None):
    """ view used to dissociate an openid from an account """
    nb_associated_openids, associated_openids = get_associate_openid(request.user)
    if nb_associated_openids == 1 and not request.user.has_usable_password() and request.method != 'GET':
        msg = ["You can't remove this openid, you should set a password first."]
        return render_to_response("authopenid/associate.html",{
                'associated_openids' : associated_openids ,
                'nb_associated_openids':nb_associated_openids,
                'msg': msg},
                context_instance = RequestContext(request)
                 )
    
    if request.POST:
        if request.POST.get('bdissociate_cancel','') ==  'Cancel':
            msg = ['Operation Cancel.']
            return redirect_to(request,'/accounts/openid/associate/')

        openid_urls = request.POST.getlist('a_openids_remove')
        if len(openid_urls) >= 1:
            for openid_url in openid_urls:
                UserAssociation.objects.get(openid_url__exact=openid_url).delete()
                if openid_url == request.session.get('openid_url'):
                    del request.session['openid_url']
                msg = "Openid removed."

            request.user.message_set.create(message = msg)
            return redirect_to(request,'/accounts/openid/associate')
    else:
        return redirect_to(request, '/accounts/openid/associate')

@login_required
def associate(request, template_name='authopenid/associate.html', 
        openid_form=AssociateOpenID, redirect_field_name='/',
        on_failure=associate_failure, extra_context=None):
    nb_associated_openids, associated_openids = get_associate_openid(request.user)
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.POST:            
        if 'a_openids' in request.POST.keys():
            a_openids = []
            if request.POST.get('a_openids','') is not '':
                a_openids = request.POST.getlist('a_openids')
                
                if len(a_openids) == nb_associated_openids and not request.user.has_usable_password():
                    if len(a_openids) > 1:
                        msg = ["You can't remove these openids, You should set a password first."]
                    else:
                        msg = ["You can't remove this openid, You should set a password first."]
                    return render('authopenid/associate.html', {
                        redirect_field_name: redirect_to,
                        'associated_openids' : associated_openids,
                        'nb_associated_openids' : nb_associated_openids,
                        'msg':msg,
                        }, context_instance=_build_context(request, extra_context=extra_context))     

                return render_to_response("authopenid/dissociate.html",{
                        'a_openids' : a_openids },
                        context_instance = RequestContext(request)
                         )
        else:
            form = openid_form(request.user, data=request.POST)
            if form.is_valid():
                if ' ' in form.cleaned_data['openid_url'] or form.cleaned_data['openid_url'] in OPENID_PROVIDER:
                    msg = ['You must enter a valid OpenID url']
                    return render('authopenid/associate.html', {
                        redirect_field_name: redirect_to,
                       'associated_openids' : associated_openids,
                        'nb_associated_openids' : nb_associated_openids,
                        'msg':msg,
                        }, context_instance=_build_context(request, extra_context=extra_context))     
                if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                    redirect_to = settings.LOGIN_REDIRECT_URL
                redirect_url = "%s%s?%s" % (
                        get_url_host(request),
                        reverse('user_complete_myassociate'),
                        urllib.urlencode({ redirect_field_name: redirect_to })
                        )
                return ask_openid(request, 
                        form.cleaned_data['openid_url'], 
                        redirect_url, 
                        on_failure=on_failure)
            else:
                msg = ['You must enter a valid OpenID url']
                return render('authopenid/associate.html', {
                    redirect_field_name: redirect_to,
                   'associated_openids' : associated_openids,
                    'nb_associated_openids' : nb_associated_openids,
                    'msg':msg,
                    }, context_instance=_build_context(request, extra_context=extra_context))     
    else:
        form = openid_form(request.user)

    msg = request.user.get_and_delete_messages()
    return render('authopenid/associate.html', {
        'form': form,
        redirect_field_name: redirect_to,
        'associated_openids' : associated_openids,
        'nb_associated_openids' : nb_associated_openids,
        'msg':msg,
    }, context_instance=_build_context(request, extra_context=extra_context))     


@login_required
def associate_success(request, identity_url, openid_response,
        redirect_field_name=REDIRECT_FIELD_NAME, send_email=True, **kwargs):
    
    openid_ = from_openid_response(openid_response)
    openids = request.session.get('openids', [])
    openids.append(openid_)
    request.session['openids'] = openids
    uassoc = UserAssociation(
                openid_url=str(openid_),
                user_id=request.user.id
    )
    uassoc.save(send_email=send_email)
    redirect_to = '/accounts/openid/associate'
    nb_associated_openids, associated_openids = get_associate_openid(request.user)
    msg = ["Your Openid has been added"]
    return render_to_response("authopenid/associate.html",{
            'associated_openids' : associated_openids ,
            'nb_associated_openids':nb_associated_openids,
            'msg': msg},
            context_instance = RequestContext(request)
             )

@csrf_exempt
@login_required
def complete_associate(request, redirect_field_name=REDIRECT_FIELD_NAME,
        template_failure='authopenid/associate.html', 
        openid_form=AssociateOpenID, redirect_name=None, 
        on_success=associate_success, on_failure=associate_failure,
        send_email=True, extra_context=None):
    if request.method == 'GET':
        return  mycomplete(request, on_success, on_failure,
                get_url_host(request) + reverse('user_complete_myassociate'),
                redirect_field_name=redirect_field_name, openid_form=openid_form, 
                template_failure=template_failure, redirect_name=redirect_name, 
                send_email=send_email, extra_context=extra_context)
    else:
        return associate(request, template_name='authopenid/associate.html', 
                openid_form=AssociateOpenID, redirect_field_name='/',
                on_failure=associate_failure, extra_context=None)

def get_associate_openid(user):
    """ get list of associated openids """
    rels = UserAssociation.objects.filter(user__id=user.id)
    associated_openids = [rel.openid_url for rel in rels]
    nb_associated_openids = len(associated_openids)
    return nb_associated_openids, associated_openids

