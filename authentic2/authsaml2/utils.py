from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.utils.translation import ugettext as _

import logging

from models import *

def is_sp_configured():
    s = get_service_provider_settings()
    if not s:
        return False
    return True

def get_service_provider_settings():
    s = MyServiceProvider.objects.all()
    if s.count() != 1:
       return None
    return s[0]

def register_next_target(request, url=None):
    session_ext = None
    try:
        session_ext = ExtendDjangoSession.objects.get(django_session_key=request.session.session_key)
        if url:
            session_ext.next = url
        else:
            next = request.GET.__getitem__('next')
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
                next = request.GET.__getitem__('next')
                session_ext.next = next
            session_ext.save()
        except:
            pass
    return session_ext

def redirect_to_target(request, key = None):
    session_ext = None
    if key:
        try:
            session_ext = ExtendDjangoSession.objects.get(django_session_key=key)
        except ExtendDjangoSession.DoesNotExist:
            pass
    else:
        try:
            session_ext = ExtendDjangoSession.objects.get(django_session_key=request.session.session_key)
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
        session_ext = ExtendDjangoSession.objects.get(django_session_key=request.session.session_key)
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
    import sys
    print >>sys.stderr, 'load_federation_temp'
    if request and login:
        try:
            session_ext = ExtendDjangoSession.objects.get(django_session_key=request.session.session_key)
            login.setIdentityFromDump(session_ext.temp_identity_dump)
            print >>sys.stderr, 'dump: ' + login.identity.dump()
        except:
            pass

