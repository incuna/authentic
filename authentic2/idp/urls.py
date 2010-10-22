from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import saml.saml2_endpoints
import saml.idff12_endpoints
from django.conf import settings
from saml.interaction import consent

urlpatterns = patterns('',)

if settings.IDP_SAML2:
    urlpatterns += patterns('',
        (r'^saml2/', include(saml.saml2_endpoints)),)

if settings.IDP_IDFF12:
    urlpatterns += patterns('',
        (r'^idff12/', include(saml.idff12_endpoints)),)

urlpatterns += patterns('',
        (r'^consent', consent),)
