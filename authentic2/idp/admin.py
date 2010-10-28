from django.contrib import admin
from django.conf import settings
from authentic2.auth.models import *

class AuthenticationEventAdmin(admin.ModelAdmin):
    date_hierarchy = 'when'

if settings.DEBUG:
    admin.site.register(AuthenticationEvent, AuthenticationEventAdmin)

