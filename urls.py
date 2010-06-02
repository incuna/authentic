from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^idp/', include('authentic.idp.urls')),
    (r'^accounts/', include('registration.urls')),
    (r'^$', login_required(direct_to_template),
        { 'template': 'index.html' }, 'index'),
)

if settings.AUTH_OPENID:
    urlpatterns += patterns('',
            (r'^account/', include('django_authopenid.urls')),)

if settings.STATIC_SERVE:
    urlpatterns += patterns('',
        url(
            regex = r'^media/(?P<path>.*)$',
            view = 'django.views.static.serve',
            kwargs = {'document_root': settings.MEDIA_ROOT}),
    )
