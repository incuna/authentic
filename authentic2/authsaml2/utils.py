import re
import datetime, time

from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from models import ExtendDjangoSession, MyServiceProvider
from django.utils.translation import ugettext as _
from django.shortcuts import render_to_response

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
    message = _('An error happened. \
        Report this %s to the administrator.') % \
            time.strftime("[%Y-%m-%d %a %H:%M:%S]", time.localtime())
    return render_to_response('error.html', {'msg': message, 'back': back},
            context_instance=RequestContext(request))

def is_sp_configured():
    s = get_service_provider_settings()
    if not s:
        return False
    return True

def get_service_provider_settings():
    s = MyServiceProvider.objects.all()
    if s.count() == 0:
       return None
    return s[0]

def register_next_target(request, url=None):
    session_ext = None
    try:
        session_ext = ExtendDjangoSession. \
            objects.get(django_session_key=request.session.session_key)
        if url:
            session_ext.next = url
        else:
            next = request.GET.get(REDIRECT_FIELD_NAME)
            session_ext.next = next
        session_ext.save()
    except:
        pass
    if not session_ext:
        try:
            session_ext = ExtendDjangoSession()
            session_ext.django_session_key = request.session.session_key
            if url:
                session_ext.next = url
            else:
                next = request.GET.get(REDIRECT_FIELD_NAME)
                session_ext.next = next
            session_ext.save()
        except:
            pass
    return session_ext

def redirect_to_target(request, key = None):
    session_ext = None
    if key:
        try:
            session_ext = ExtendDjangoSession. \
                objects.get(django_session_key=key)
        except ExtendDjangoSession.DoesNotExist:
            pass
    else:
        try:
            session_ext = ExtendDjangoSession. \
                objects.get(django_session_key=request.session.session_key)
        except ExtendDjangoSession.DoesNotExist:
            pass
    if session_ext:
        if session_ext.next:
            return HttpResponseRedirect(session_ext.next)
    return HttpResponseRedirect("/")

# Used because an identity dump must be temporary stored for account linking
def save_federation_temp(request, login):
    if not request or not login:
        return None
    session_ext = None
    try:
        session_ext = ExtendDjangoSession. \
            objects.get(django_session_key=request.session.session_key)
        session_ext.temp_identity_dump = login.identity.dump()
        session_ext.save()
    except:
        pass
    if not session_ext:
        try:
            session_ext = ExtendDjangoSession()
            session_ext.django_session_key = request.session.session_key
            session_ext.temp_identity_dump = login.identity.dump()
            session_ext.save()
        except:
            pass
    return session_ext

def load_federation_temp(request, login):
    if request and login:
        try:
            session_ext = ExtendDjangoSession. \
                objects.get(django_session_key=request.session.session_key)
            login.setIdentityFromDump(session_ext.temp_identity_dump)
        except:
            pass
