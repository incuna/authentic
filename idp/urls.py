from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import saml.saml2_endpoints
from django.conf import settings

urlpatterns = patterns('',)

if settings.IDP_SAML2:
    urlpatterns += patterns('',
        (r'^saml2/', include(saml.saml2_endpoints)),)
