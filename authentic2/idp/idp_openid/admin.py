# -*- coding: utf-8 -*-

from django.contrib import admin
from models import TrustedRoot, Association, Nonce

admin.site.register(TrustedRoot)
admin.site.register(Association)
admin.site.register(Nonce)
