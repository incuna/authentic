from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from signals import auth_login
from signals import auth_logout
from signals import auth_oidlogin
from django.conf import settings
from admin_log_view.models import info
from django.contrib.auth.models import User
import settings

REGISTERED_SERVICE_LIST = []

def register_service_list(list_or_callable):
    '''Register a list of tuple (uri, name) to present in user service list, or
       a callable which will receive the request object and return a list of tuples.
    '''
    REGISTERED_SERVICE_LIST.append(list_or_callable)

def service_list(request):
    '''Compute the service list to show on user homepage'''
    list = []
    for list_or_callable in REGISTERED_SERVICE_LIST:
        if callable(list_or_callable):
            list += list_or_callable(request)
        else:
            list += list_or_callable
    return list

def homepage(request):
    '''Homepage of the IdP'''
    import authentic.saml.common
    import authentic.authsaml2.utils
    tpl_parameters = {}
    tpl_parameters['authorized_services'] = service_list(request)
    if authentic.authsaml2.utils.is_sp_configured():
        tpl_parameters['provider_active_session'] = authentic.saml.common.get_provider_of_active_session(request)
        tpl_parameters['provider_name'] = authentic.saml.common.get_provider_of_active_session_name(request)
    if settings.IDP_OPENID:
        tpl_parameters['openid'] = request.user.openid_set
        tpl_parameters['IDP_OPENID'] = settings.IDP_OPENID
    return render_to_response('index.html', tpl_parameters, RequestContext(request))

def LogRegistered(sender, user, **kwargs):
    msg = user.username + ' is now registered'
    info(msg)

def LogActivated(sender, user, **kwargs):
    msg = user.username + ' has activated his account'
    info(msg)

def LogRegisteredOI(sender, openid, **kwargs):
    msg = openid 
    msg = str(msg) + ' is now registered'
    info(msg)

def LogAssociatedOI(sender, user, openid, **kwargs):
    msg = user.username + ' has associated his user with ' + openid
    info(msg)

def LogAuthLogin(sender, user, successful, **kwargs):
    if successful:
        msg = user.username + ' has logged in with success'
    else:    
        msg = user + ' has tried to login without success'
    info(msg)

def LogAuthLogout(sender, user, **kwargs):
    msg = str(user) 
    msg += ' has logged out'
    info(msg)

def LogAuthLoginOI(sender, openid_url, state, **kwargs):
    msg = str(openid_url)
    if state is 'success':
        msg += ' has login with success with OpenID'
    elif state is 'invalid':
        msg += ' is invalid'
    elif state is 'not_supported':
        msg += ' did not support i-names'
    elif state is 'cancel':
        msg += ' has cancel'
    elif state is 'failure':
        msg += ' has failed'
    elif state is 'setup_needed':
        msg += ' setup_needed'
    info(msg)

def admin_service(request):
    if request.user.is_staff:
        return (('/admin', _('Authentic administration')),)
    return []

register_service_list(admin_service)

auth_login.connect(LogAuthLogin, dispatch_uid = "authentic.idp")
auth_logout.connect(LogAuthLogout, dispatch_uid = "authentic.idp")
auth_oidlogin.connect(LogAuthLoginOI, dispatch_uid ="authentic.idp")

if settings.AUTH_OPENID:
    from django_authopenid.signals import oid_register
    from django_authopenid.signals import oid_associate
    oid_register.connect(LogRegisteredOI, dispatch_uid = "authentic.idp")
    oid_associate.connect(LogAssociatedOI, dispatch_uid = "authentic.idp")

