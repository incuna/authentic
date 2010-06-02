from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import saml.saml2_endpoints

urlpatterns = patterns('',
    (r'^saml2/', include(saml.saml2_endpoints)),
)

