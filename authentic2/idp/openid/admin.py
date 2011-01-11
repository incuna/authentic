# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 : */

from django.contrib import admin
from models import TrustedRoot, Association, Nonce

admin.site.register(TrustedRoot)
admin.site.register(Association)
admin.site.register(Nonce)
