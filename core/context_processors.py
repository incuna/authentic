from django.conf import settings

def auth_settings(request):
    return {
        'HAS_AUTH_OPENID': settings.AUTH_OPENID,
        'HAS_AUTH_SSL': settings.AUTH_SSL,
    }


def No_Home_Url(request):
    return {'NO_HOME_URL': settings.NO_HOME_URL}
