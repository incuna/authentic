from django.contrib import admin
from django.conf import settings

from models import AttributeItem, AttributeList, AttributePolicy, \
    UserConsentAttributes


class AttributeListAdmin(admin.ModelAdmin):
    filter_horizontal = ('attributes', )
    fieldsets = (
            (None, {
                'fields' : (
                    'name',
                    'attributes',
                )
            }),
    )


class AttributePolicyAdmin(admin.ModelAdmin):
    filter_horizontal = ('source_filter_for_sso_from_push_sources', )
    fieldsets = (
            (None, {
                'fields' : (
                    'name',
                    'enabled',
                    'ask_consent_attributes',
                    'allow_attributes_selection',
                    'attribute_list_for_sso_from_pull_sources',
                    'forward_attributes_from_push_sources',
                    'map_attributes_from_push_sources',
                    'output_name_format',
                    'output_namespace',
                    'source_filter_for_sso_from_push_sources',
                    'attribute_filter_for_sso_from_push_sources',
                    'filter_source_of_filtered_attributes',
                    'map_attributes_of_filtered_attributes',
                    'send_error_and_no_attrs_if_missing_required_attrs',
                )
            }),
    )



admin.site.register(AttributeItem)
admin.site.register(AttributeList, AttributeListAdmin)
admin.site.register(AttributePolicy, AttributePolicyAdmin)

if settings.DEBUG:
    admin.site.register(UserConsentAttributes)
