from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import liberty.saml2_endpoints

urlpatterns = patterns('',
    (r'^saml/', include(liberty.saml2_endpoints)),
)

