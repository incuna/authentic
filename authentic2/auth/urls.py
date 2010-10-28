from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'login/$', 'authentic2.auth.views.login'),
    (r'password/change/$','authentic2.auth.views.password_change'),
    (r'$', include('registration.urls')),
)

if settings.AUTH_OPENID:
    urlpatterns += patterns('',
            (r'^accounts/openid/', include('authentic2.auth.openid.urls')),
    )
