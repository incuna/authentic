from django.conf.urls.defaults import *

from saml2_endpoints import *

urlpatterns = patterns('',
    (r'^metadata$', metadata),
    # Receive request from user interface
    (r'^sso$', sso),
    (r'^finish_federation$', finish_federation),
    (r'^singleSignOnArtifact$', singleSignOnArtifact),
    (r'^singleSignOnPost$', singleSignOnPost),
    # Receive request from user interface
    (r'^logout$', logout),
    # Receive response from Redirect SP initiated
    (r'^singleLogoutReturn$', singleLogoutReturn),
    # Receive request from SOAP IdP initiated
    (r'^singleLogoutSOAP$', singleLogoutSOAP),
    # Receive request from Redirect IdP initiated
    (r'^singleLogout$', singleLogout),
    # Receive request from user interface
    (r'^federationTermination/(?P<entity_id>[a-zA-Z0-9\:\-\./]+)/$', federationTermination),
    # Receive response from Redirect SP initiated
    (r'^manageNameIdReturn$', manageNameIdReturn),
    # Receive request from SOAP IdP initiated
    (r'^manageNameIdSOAP$', manageNameIdSOAP),
    # Receive request from Redirect IdP initiated
    (r'^manageNameId$', manageNameId),
)
