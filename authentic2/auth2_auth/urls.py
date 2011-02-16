from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'login/$', 'authentic2.auth2_auth.views.login'),
    (r'password/change/$','authentic2.auth2_auth.views.password_change'),
    (r'$', include('registration.urls')),
)

if settings.AUTH_OPENID:
    urlpatterns += patterns('',
        (r'^accounts/openid/',
            include('authentic2.auth2_auth.auth2_openid.urls')),
    )

if settings.AUTH_SSL:
    urlpatterns += patterns('',
        url(r'^sslauth/$',
            'authentic2.auth2_auth.auth2_ssl.login_ssl.handle_request',
            name='user_signin_ssl'),
        url(r'^sslauth/post_account_linking$',
            'authentic2.auth2_auth.auth2_ssl.login_ssl.post_account_linking'),
        url(r'^sslauth/delete_certificate$',
            'authentic2.auth2_auth.auth2_ssl.login_ssl.delete_certificate'),
        url(r'^sslauth/register/$',
            'authentic2.auth2_auth.auth2_ssl.views.register'),
        url(r'^error_ssl/$', direct_to_template,
            {'template': 'error_ssl.html'}, 'error_ssl'),
    )
