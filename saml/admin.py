from django.contrib import admin
from django.utils.translation import ugettext as _
from models import *

class LibertyProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_id', 'protocol_conformance')
    list_display_links = ('entity_id',)
    list_editable = ('name',)
    search_fields = ('name', 'entity_id')
    readonly_fields = ('entity_id','protocol_conformance')
    fieldsets = (
            (None, { 'fields' : ('name', 'entity_id') }),
            (_('Metadata files'),
                { 'fields': ('metadata', 'public_key', 'ssl_certificate', 'ca_cert_chain') }))

class LibertyAttributeMappingInline(admin.TabularInline):
    model = LibertyAttributeMapping

class LibertyAttributeMapAdmin(admin.ModelAdmin):
    inlines = [
            LibertyAttributeMappingInline,
    ]

admin.site.register(LibertyProvider, LibertyProviderAdmin)
admin.site.register(LibertyAttributeMap, LibertyAttributeMapAdmin)
