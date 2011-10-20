.. _attributes_in_session:

==============================================================
Attributes in session pushed by third SAML2 identity providers
==============================================================

When an assertion is received, assertion data, including attributes, are
pushed in the Django session dictionnary.

It leads to the creation of the following dictionnary::

    request.session['multisource_attributes']

The keys of the dictionnary are the source names, i.e. the entity Id for
SAML2 identity providers.

The values are list of data extracted from assertions. Indeed, this is done
to store multiple assertion received from a same source in a same Django
session::

    request.session['multisource_attributes'] \
        [source_name] = list()

The items of this list are dictionnaries with the keys 'certificate_type' and
'attributes'.

For a saml2 assertion, all the keys are::

    a8n['certificate_type'] = 'SAML2_assertion'
    a8n['nameid'] = ...
    a8n['subject_confirmation_method'] = ...
    a8n['not_before'] = ...
    a8n['not_on_or_after'] = ...
    a8n['authn_context'] = ...
    a8n['authn_instant'] = ...
    a8n['attributes'] = attrs

a8n['attributes'] has the following structure::

    attributes = {}
    attributes[name] = (value1, value2, )
    attributes[(name, format)] = (value1, value2, )
    attributes[(name, format, nickname)] = (value1, value2, )
    a8n['attributes'] = attributes
