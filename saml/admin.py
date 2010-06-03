from django.contrib import admin
from django.utils.translation import ugettext as _
from models import *

class LibertyProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_id', 'protocol_conformance')
    fieldsets = (
            (None, { 'fields' : ('name', ) }),
            (_('Metadata files'),
                { 'fields': ('metadata', 'public_key', 'ssl_certificate', 'ca_cert_chain') }))


admin.site.register(LibertyProvider, LibertyProviderAdmin)
