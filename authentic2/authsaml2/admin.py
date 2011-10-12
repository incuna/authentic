from django.contrib import admin
from models import MyServiceProvider

class MyServiceProviderAdmin(admin.ModelAdmin):
    fieldsets = (
            (None, {
                'fields' : (
                    'handle_persistent',
                    'handle_transient',
                    'back_url',
                )
            }),
    )

admin.site.register(MyServiceProvider, MyServiceProviderAdmin)
