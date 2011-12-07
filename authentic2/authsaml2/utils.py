import re
import time
import logging

from django.template import RequestContext
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response
from django.contrib import messages
from django.conf import settings

__redirection_timeout = 1600

__root_refererer_re = re.compile('^(https?://[^/]*/?)')
def error_page(request, message=None, back=None, logger=None,
            default_message=True, timer=False):
    '''View that show a simple error page to the user with a back link.

         back - url for the back link, if None, return to root of the referer
                or the local root.
    '''
    if logger:
        logger.error('Showing message %r on an error page' % message)
    else:
        logging.error('Showing message %r on an error page' % message)
    if back is None:
        referer = request.META.get('HTTP_REFERER')
        if referer:
            root_referer = __root_refererer_re.match(referer)
            if root_referer:
                back = root_referer.group(1)
        if back is None:
            back = '/'
    global __redirection_timeout
    context = RequestContext(request)
    if timer:
        context['redir_timeout'] = __redirection_timeout
        context['next_page'] = back
    display_message = getattr(settings, 'DISPLAY_MESSAGE_ERROR_PAGE', ())
    if default_message and not display_message:
        messages.add_message(request, messages.ERROR,
            _('An error happened. Report this %s to the administrator.') % \
                time.strftime("[%Y-%m-%d %a %H:%M:%S]", time.localtime()))
    elif message:
        messages.add_message(request, messages.ERROR, message)
    return render_to_response('error_authsaml2.html', {'back': back},
            context_instance=context)

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
    if 'next' in request.session:
        return request.session['next']
    return None

def register_request_id(request, request_id):
    request.session['saml_request_id'] = request_id

def check_response_id(request, login):
    if 'saml_request_id' in request.session and \
        request.session['saml_request_id'] == login.response.inResponseTo:
        return True
    return False

# Used for account linking
def save_federation_temp(request, login, attributes=None):
    if login and login.identity:
        request.session['identity_dump'] = login.identity.dump()
    request.session['remoteProviderId'] = login.remoteProviderId
    if attributes:
        request.session['attributes'] = attributes

def load_federation_temp(request, login):
    if 'identity_dump' in request.session:
        login.setIdentityFromDump(request.session['identity_dump'])
