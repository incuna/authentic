import urllib
import string
import random

from django.contrib.auth.models import User
from django.views.generic.simple import redirect_to
from django.http import HttpResponseBadRequest
from django.template import RequestContext
from django.template.loader import render_to_string

import models
import authentic2.vendor.totp_js.totp_bookmarklet as totp_bookmarklet

_hexachars = '0123456789abcdef'

def new_totp_secret(request, next='/'):
    if request.user is None or not hasattr(request.user, '_meta') \
       or request.method != 'POST':
        return HttpResponseBadRequest()
    key = ''.join([random.choice(_hexachars) for x in range(40)])
    print 'key', key, len(key)
    secret, _ = models.OATHTOTPSecret.objects.get_or_create(user=request.user)
    secret.key = key
    secret.save()
    next = request.REQUEST.get('next',next)
    return redirect_to(request, next)

def delete_totp_secret(request, next='/'):
    if request.user is None or not hasattr(request.user, '_meta') \
       or request.method != 'POST':
        return HttpResponseBadRequest()
    try:
        models.OATHTOTPSecret.objects.filter(user=request.user).delete()
    except models.OATHTOTPSecret.DoesNotExist:
        pass
    next = request.REQUEST.get('next',next)
    return redirect_to(request, next)

def totp_profile(request, next='', template_name='oath/totp_profile.html'):
    if request.user is None or not hasattr(request.user, '_meta'):
        return ''
    if next:
        next = '?next=%s' % urllib.quote(next)
    key, bookmarklet = '', ''
    try:
        secret = models.OATHTOTPSecret.objects.get(user=request.user)
        key = secret.key
        bookmarklet = totp_bookmarklet.otp_doc(secret.key)
    except models.OATHTOTPSecret.DoesNotExist:
        pass
    return render_to_string(template_name,
            { 'key': key, 
              'bookmarklet': bookmarklet, 
              'next': next,
              'base': '/oath'},
            RequestContext(request))
