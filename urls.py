from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from authentic.idp import homepage
import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/admin_log_view/log/', 'admin_log_view.views.admin_view'),
    (r'^admin/', include(admin.site.urls)),
    (r'^idp/', include('authentic.idp.urls')),
    (r'^$', login_required(homepage), {}, 'index'),
)

if settings.AUTH_OPENID:
    urlpatterns += patterns('',
            (r'^accounts/openid/$', 'django.views.generic.simple.redirect_to', {'url': '..'}),
            (r'^accounts/openid/', include('django_authopenid.urls')),
    )

urlpatterns += patterns('',
    (r'^accounts/logout/', 'idp.views.AuthLogout'),
    (r'^accounts/$', 'django.views.generic.simple.redirect_to', {'url': '..'}),
    (r'^accounts/', include('registration.urls')),
)

urlpatterns += patterns('',
    (r'^authsaml2/', include('authentic.authsaml2.urls')),
)

if settings.AUTH_SSL:
    urlpatterns += patterns('',
        url(r'^sslauth/$',
            'authentic.sslauth.login_ssl.process_request',
            name='user_signin_ssl'),
        url(r'^error_ssl/$', direct_to_template,
            {'template': 'error_ssl.html'}, 'error_ssl'),
    )

if settings.STATIC_SERVE:
    urlpatterns += patterns('',
        url(
            regex = r'^media/(?P<path>.*)$',
            view = 'django.views.static.serve',
            kwargs = {'document_root': settings.MEDIA_ROOT}),
    )
