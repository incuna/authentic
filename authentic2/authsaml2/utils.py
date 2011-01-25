import re
import datetime, time

from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from models import MyServiceProvider
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.contrib.sessions.models import Session

__root_refererer_re = re.compile('^(https?://[^/]*/?)')
def error_page(request, message, back = None, logger = None):
    '''View that show a simple error page to the user with a back link.

         back - url for the back link, if None, return to root of the referer
                or the local root.
    '''
    if logger:
        logger.error('[authsaml2] %s - Return error page' % message)
    else:
        logging.error('[authsaml2] %s - Return error page' % message)
    if back is None:
        referer = request.META.get('HTTP_REFERER')
        if referer:
            root_referer = __root_refererer_re.match(referer)
            if root_referer:
                back = root_referer.group(1)
        if back is None:
            back = '/'
    #message = _('An error happened. \
    #    Report this %s to the administrator.') % \
    #        time.strftime("[%Y-%m-%d %a %H:%M:%S]", time.localtime())
    return render_to_response('error.html', {'msg': message, 'back': back},
            context_instance=RequestContext(request))

def is_sp_configured():
    cfg = MyServiceProvider.objects.all()
    if not cfg or not cfg[0]:
        return False
    return True

def get_service_provider_settings():
    cfg = MyServiceProvider.objects.all()
    if not cfg or not cfg[0]:
       return None
    return cfg[0]

# Used to register requested url during SAML redirections
def register_next_target(request, url=None):
    if url:
        next = url
    else:
        next = request.GET.get(REDIRECT_FIELD_NAME)
        if not next:
            next = '/'
    request.session['next'] = next

def get_registered_url(request):
    if request.session.has_key('next'):
        return request.session['next']
    return None

def register_request_id(request, request_id):
    request.session['saml_request_id'] = request_id

def check_response_id(request, login):
    if request.session.has_key('saml_request_id') and \
        request.session['saml_request_id'] == login.response.inResponseTo:
        return True
    return False

# Used for account linking
def save_federation_temp(request, login):
    if login and login.identity:
        request.session['identity_dump'] = login.identity.dump()

def load_federation_temp(request, login):
    if request.session.has_key('identity_dump'):
        login.setIdentityFromDump(request.session['identity_dump'])
