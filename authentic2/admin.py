from django.contrib import admin

from .nonce.models import Nonce

class NonceModelAdmin(admin.ModelAdmin):
    list_display = ("value", "context", "not_on_or_after")

admin.site.register(Nonce, NonceModelAdmin)
