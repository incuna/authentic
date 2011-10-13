.. _config_saml2_sp:

====================================
Configure SAML 2.0 service providers
====================================

How to I authenticate against Authentic2 with a SAMLv2 service provider ?
-------------------------------------------------------------------------

1. Grab the SAML2 IdP metadata:

    http[s]://your.domain.com/idp/saml2/metadata

2. And configure your service provider with it.

3. Go to the providers admin panel on:

    http[s]://your.domain.com/admin/saml/libertyprovider/add/

There create a new provider using the service provider metadata and enable it
as a service provider, you can customize some behaviours like the preferred
assertion consumer or encryption for the NameID or the Assertion element.

