import re
import datetime, time

from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from models import ExtendDjangoSession, MyServiceProvider
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
    message = _('An error happened. \
        Report this %s to the administrator.') % \
            time.strftime("[%Y-%m-%d %a %H:%M:%S]", time.localtime())
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
    if not request:
        return None
    session_ext = None
    if url:
        next = url
    else:
        next = request.GET.get(REDIRECT_FIELD_NAME)

    try:
        s = Session.objects.get(pk=request.session.session_key)
        session_ext = ExtendDjangoSession. \
            objects.get(session=s)
        session_ext.next = next
        session_ext.save()
    except:
        pass

    if not session_ext:
        try:
            s = Session.objects.get(pk=request.session.session_key)
            session_ext = ExtendDjangoSession(session=s, next=next)
            session_ext.save()
        except:
            pass

    return session_ext

def get_registered_url(request):
    if not request:
        return None
    cfg = MyServiceProvider.objects.all()
    if not cfg or not cfg[0]:
        return '/'

    session_ext = None

    try:
        s = Session.objects.get(pk=request.session.session_key)
        session_ext = ExtendDjangoSession. \
            objects.get(session=s)
    except ExtendDjangoSession.DoesNotExist:
        pass

    if session_ext:
        if session_ext.next:
            return session_ext.next

    if cfg[0].back_url:
        return cfg[0].back_url

    return '/'

###
 # register_federation_in_progres
 # @request
 # @nameId
 #
 # Register the post-authnrequest process during account linking
 ###
def register_federation_in_progress(request, nameId):
    if not request or not nameId:
        return None
    session_ext = None
    try:
        s = Session.objects.get(pk=request.session.session_key)
        session_ext = ExtendDjangoSession. \
            objects.get(session=s)
        session_ext.federation_in_progress = nameId
        session_ext.save()
    except:
        pass
    if not session_ext:
        try:
            s = Session.objects.get(pk=request.session.session_key)
            session_ext = ExtendDjangoSession(session=s)
            session_ext.federation_in_progress = nameId
            session_ext.save()
        except:
            pass 
    return session_ext

# Used because an identity dump must be temporary stored for account linking
def save_federation_temp(request, login):
    if not request or not login:
        return None
    session_ext = None
    try:
        s = Session.objects.get(pk=request.session.session_key)
        session_ext = ExtendDjangoSession. \
            objects.get(session=s)
        session_ext.temp_identity_dump = login.identity.dump()
        session_ext.save()
    except:
        pass
    if not session_ext:
        try:
            s = Session.objects.get(pk=request.session.session_key)
            session_ext = ExtendDjangoSession(session=s)
            session_ext.temp_identity_dump = login.identity.dump()
            session_ext.save()
        except:
            pass
    return session_ext

def load_federation_temp(request, login):
    if request and login:
        try:
            session_ext = ExtendDjangoSession. \
                objects.get(session=request.session)
            login.setIdentityFromDump(session_ext.temp_identity_dump)
        except:
            pass
