from django.contrib import admin
from django.utils.translation import ugettext as _
from django.conf import settings
from django.forms import ModelForm
from django.forms.widgets import MultiWidget
import django.forms
from models import *

class LibertyServiceProviderInline(admin.StackedInline):
    model = LibertyServiceProvider

class LibertyIdentityProviderInline(admin.StackedInline):
    model = LibertyIdentityProvider
    fieldsets = (
            (None, {
                'fields' : (
                    'enabled',
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
                    'attribute_map'
                )
            }),
    )

class TextAndFileWidget(django.forms.widgets.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (django.forms.widgets.Textarea(),
                django.forms.widgets.FileInput(),)
        super(TextAndFileWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        return (value, None)

    def value_from_datadict(self, data, files, name):
        # If there is a file input use it
        file = self.widgets[1].value_from_datadict(data, files, name + '_1')
        if file:
            file = file.read(file.size)
        if file:
            value = file
        else:
            value = self.widgets[0].value_from_datadict(data, files, name + '_0')
        return value

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        if isinstance(value, (str, unicode)):
            attrs['rows'] = value.count('\n') + 5
            attrs['cols'] = min(max((len(x) for x in value.split('\n'))), 150)
        return super(TextAndFileWidget, self).render(name, value, attrs)


class LibertyProviderForm(ModelForm):
    metadata = django.forms.CharField(required=True,widget=TextAndFileWidget)
    public_key = django.forms.CharField(required=False,widget=TextAndFileWidget)
    ssl_certificate = django.forms.CharField(required=False,widget=TextAndFileWidget)
    ca_cert_chain = django.forms.CharField(required=False,widget=TextAndFileWidget)
    class Meta:
        model = LibertyProvider

class LibertyProviderAdmin(admin.ModelAdmin):
    form = LibertyProviderForm
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
    admin.site.register(LibertySession)
    admin.site.register(LibertyAssertion)
    admin.site.register(LibertySessionSP)
    admin.site.register(KeyValue)
