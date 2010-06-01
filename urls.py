from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^registration/', include('registration.urls')),
    (r'^$', direct_to_template,
        { 'template': 'index.html' }, 'index'),
)
