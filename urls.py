from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.urls')),
    (r'^account/', include('django_authopenid.urls')),
    (r'^$', login_required(direct_to_template),
        { 'template': 'index.html' }, 'index'),
)

if settings.STATIC_SERVE:
    urlpatterns += patterns('',
        url(
            regex = r'^media/(?P<path>.*)$',
            view = 'django.views.static.serve',
            kwargs = {'document_root': settings.MEDIA_ROOT}),
    )
