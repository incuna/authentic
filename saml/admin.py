from django.contrib import admin
from django.utils.translation import ugettext as _
from django.conf import settings
from models import *

class LibertyServiceProviderInline(admin.StackedInline):
    model = LibertyServiceProvider

class LibertyIdentityProviderInline(admin.StackedInline):
    model = LibertyIdentityProvider
    fieldsets = (
            (None, {
                'fields' : (
                    'enabled',
                    ('enable_binding_for_sso_response', 'binding_for_sso_response'),
                    ('enable_http_method_for_slo_request', 'http_method_for_slo_request'),
                    ('enable_http_method_for_defederation_request', 'http_method_for_defederation_request'),
                    'want_authn_request_signed',
                    'attribute_map'
                )
            }),
    )

class LibertyProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_id', 'protocol_conformance')
    list_display_links = ('entity_id',)
    list_editable = ('name',)
    search_fields = ('name', 'entity_id')
    readonly_fields = ('entity_id','protocol_conformance')
    fieldsets = (
            (None, {
                'fields' : ('name', 'entity_id')
            }),
            (_('Metadata files'), {
                'fields': ('metadata', 'public_key', 'ssl_certificate', 'ca_cert_chain')
            }),
    )
    inlines = [
            LibertyServiceProviderInline,
            LibertyIdentityProviderInline
    ]

admin.site.register(LibertyProvider, LibertyProviderAdmin)

if settings.DEBUG:
    admin.site.register(LibertySessionDump)
    admin.site.register(LibertyIdentityDump)
    admin.site.register(LibertyFederation)
    admin.site.register(LibertySessionSP)
