from django.contrib import admin
from models import UserConsentAttributes
from django.conf import settings

if settings.DEBUG:
    admin.site.register(UserConsentAttributes)
