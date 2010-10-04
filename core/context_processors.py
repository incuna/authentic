from django.conf import settings

def auth_settings(request):
    return {
        'HAS_AUTH_OPENID': settings.AUTH_OPENID,
        'HAS_AUTH_SSL': settings.AUTH_SSL,
    }

