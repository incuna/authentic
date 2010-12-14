from django.contrib import admin
from models import *

#admin.site.register(MyServiceProvider)

class MyServiceProviderAdmin(admin.ModelAdmin):
    fieldsets = (
            (None, {
                'fields' : (
                    'handle_persistent',
                    'handle_transient',
                    'back_url',
                    'activate_default_sp_policy',
                    'no_nameid_policy',
                    'requested_name_id_format',
                    'allow_create',
                    ('enable_binding_for_sso_response', 'binding_for_sso_response'),
                    ('enable_http_method_for_slo_request', 'http_method_for_slo_request'),
                    ('enable_http_method_for_defederation_request', 'http_method_for_defederation_request'),
                    'user_consent',
                    'want_force_authn_request',
                    'want_is_passive_authn_request',
                    'want_authn_request_signed',
                )
            }),
    )

admin.site.register(MyServiceProvider, MyServiceProviderAdmin)

