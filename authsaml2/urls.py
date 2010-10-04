from django.conf.urls.defaults import *

from saml2_endpoints import *

urlpatterns = patterns('',
    (r'^metadata$', metadata),
    (r'^sso', sso),
    (r'^finish_federation', finish_federation),
    (r'^selectProvider/(?P<entity_id>[a-zA-Z0-9\:\-\./]+)/$', selectProvider),
    (r'^singleSignOnArtifact', singleSignOnArtifact),
    (r'^singleSignOnPost', singleSignOnPost),
    (r'^logout', logout),
    (r'^singleLogoutReturn', singleLogoutReturn),
    (r'^singleLogoutSOAP', singleLogoutSOAP),
    (r'^singleLogout', singleLogout),
    (r'^federationTermination/(?P<entity_id>[a-zA-Z0-9\:\-\./]+)/$', federationTermination),
    (r'^saml/manageNameIdReturn', manageNameIdReturn),
)
