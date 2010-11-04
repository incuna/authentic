import functools

import registration.views
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings

import forms

def register(request):
    '''Registration page for SSL auth without CA'''
    next = request.GET.get(REDIRECT_FIELD_NAME, settings.LOGIN_REDIRECT_URL)
    print 'toto', request.method
    return registration.views.register(request, success_url=next,
            form_class=functools.partial(forms.RegistrationForm,
                request=request))

