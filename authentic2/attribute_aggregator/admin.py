from django.contrib import admin

from models import AttributeSource, UserAliasInSource

class LdapSourceAdmin(admin.ModelAdmin):
    fieldsets = (
            (None, {
                'fields' : (
                    'name',
                    'server',
                    'user',
                    'password',
                    'base',
                    'port',
                    'ldaps',
                    'certificate',
                    'is_auth_backend',
                )
            }),
    )

admin.site.register(AttributeSource)
admin.site.register(UserAliasInSource)

try:
    from models import LdapSource
    admin.site.register(LdapSource, LdapSourceAdmin)
except ImportError:
    pass
