from django.conf.urls.defaults import patterns

from saml2_endpoints import metadata, sso, finish_federation, \
    singleSignOnArtifact, singleSignOnPost, sp_slo, logout, singleLogoutReturn, \
    singleLogoutSOAP, singleLogout, federationTermination, manageNameIdReturn, \
    manageNameIdSOAP, manageNameId, delete_federation

urlpatterns = patterns('',
    (r'^metadata$', metadata),
    # Receive request from user interface
    (r'^sso$', sso),
    (r'^finish_federation$', finish_federation),
    (r'^singleSignOnArtifact$', singleSignOnArtifact),
    (r'^singleSignOnPost$', singleSignOnPost),
    # Receive request from functions
    (r'^sp_slo/(.*)$', sp_slo),
    # Receive request from user interface
    (r'^logout$', logout),
    # Receive response from Redirect SP initiated
    (r'^singleLogoutReturn$', singleLogoutReturn),
    # Receive request from SOAP IdP initiated
    (r'^singleLogoutSOAP$', singleLogoutSOAP),
    # Receive request from Redirect IdP initiated
    (r'^singleLogout$', singleLogout),
    # Receive request from user interface
    (r'^federationTermination$', federationTermination),
    # Receive response from Redirect SP initiated
    (r'^manageNameIdReturn$', manageNameIdReturn),
    # Receive request from SOAP IdP initiated
    (r'^manageNameIdSOAP$', manageNameIdSOAP),
    # Receive request from Redirect IdP initiated
    (r'^manageNameId$', manageNameId),
    # Receive request from Redirect IdP initiated
    (r'^delete_federation$', delete_federation),
)
