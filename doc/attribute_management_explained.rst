.. _attribute_management_explained:

Attribute management machinery explained (attribute_aggregator module)
======================================================================

Attribute aggegrator module
---------------------------

The core attribute management is based on the attribute aggregator module.

Intro
_____

Attribute aggregator provides a main Model class called UserAttributeProfile,
functions to load attributes and extract attributes.

The mapping between attribute namespaces is built-in and depends on a unique
file (mapping.py).

A main schema is defined and is based on LDAP/X500 for naming. The support
of http://schemas.xmlsoap.org/ws/2005/05/identity/claims is partly complete.

Source of attributes are connected with attribute loading functions using
signals.

FAQ
___

Why not use the Django User profile?

The django user profile needs to define attributes as class attributes and
then support form filling or mapping with LDAP.

That is useful and may be used, especially because the profile can be used as
a source of attribute to load in the attribute_aggregator profile.

The attribute_aggregator profile allow to load multivalued attributes from any
source supported (LDAP, Django profile and attributes in Django session for
now) from any namespace defined in mapping.py (LDAP/X500 and claims for now).

The profile can be loaded giving a source or a list of attribute, or can be
from any known source, or with a dictionnary.

Attributes can be extracted with many functions in any namespace supported.

Quick explanation
_________________

The schema is defined in mapping.py and is made of definitions like this::

    "sn": {
        "oid": "2.5.4.4",
        "display_name": _("sn surname"),
        "alias": ['surname'],
        "profile_field_name": 'last_name',
        "type": "http://www.w3.org/2001/XMLSchema#string",
        "namespaces": {
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims": {
                "identifiers":
                    [
            "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname",
                    ],
                "friendly_names":
                    [
                "Last Name",
                    ],
            }
        }
    },

The profile store all the data in a text field taht contains a cPickle list of
instances of the class AttributeData.

The profile is attached to a user and then can be created or loaded with::

    profile = load_or_create_user_profile(user=user)

User may be None to create a temporary profile for an anonymous user. But
that need a DB cleaning function not implemented.

The model *UserAttributeProfile*
________________________________

The model 'UserAttributeProfile' can be attached to a user and then persist
(as a Model).

When the profile is loaded, all data stored are removed expect if the
the data has an expiration date later.

The profile provide several methods to store and extract attributes.

All the methods to add attributes are based on a main one accepting a
dictionnary of attribute is parameters 'load_by_dic()'. The other methods
('load_listed_attributes()', 'load_greedy()') send a signal with a list of
attributes (listed_attributes_call) or not (any_attributes_call) to grab a
dictionnary. The list is given with the definition name, oid or friendly name
of the attribute in the system namespace.

Into the dictionnary, attributes are given with their name, oid or friendly
name in the default namespace or with their name in a namepsace. An expiration
date can also be given (ISO8601 format), if none, attribute will be deleted at
next profile loading. The dictionnary format is as follows::

    attributes = dict()
    data_from_source = list()
    a1 = dict()
        a1['oid'] = definition_name
    Or
        a1['definition'] = definition_name
            definition may be the definition name like 'gn'
            or an alias like 'givenName'
    Or
        a1['name'] = attribute_name_in_ns
        a1['namespace'] = ns_name
    a1['expiration_date'] = date
    a1['values'] = list_of_values
    data_from_source.append(a1)
    ...
    data_from_source.append(a2)
    attributes[source_name] = data_from_source

Getters are defined to extract data from a profile. Only AttributeData
instances are extracted that assume that any attribute namespace can be used.

* get_data_of_definition(definition)

Return a list of AttributeData instances corresponding to the definition
given.

* get_freshest_data_of_definition(definition)

Return the freshest AttributeData instance. If multiple with no or same exp
date, random. Should use the creation date soon.

* get_data_of_source

Return a list of AttributeData instances corresponding to the source given.

* get_data_of_source_by_name

Idem but source name is given, not a Source instance.

* get_data_of_definition_and_source

Return a list of AttributeData instances corresponding to the definition and
source given.

* get_data_of_definition_and_source_by_name

Idem but source name is given, not a Source instance.

SAML2 attribute representation in assertions
--------------------------------------------

SAML2 attribute profile (saml-profiles-2.0-os - Section 8) defines two kind of
attribute element syntax in the attribute statement of assertions, also
called *name format*:

- BASIC::

    NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"

- URI::

    NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"

*URI should be used when attributes have "universally" known unique names
like OID.*

Example::

    <saml:Attribute NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"
        Name="FirstName">
        <saml:AttributeValue xsi:type="xs:string">By-Tor</saml:AttributeValue>
    </saml:Attribute>

    <saml:Attribute
        xmlns:x500="urn:oasis:names:tc:SAML:2.0:profiles:attribute:X500"
        NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"
        Name="urn:oid:2.5.4.42" FriendlyName="givenName">
        <saml:AttributeValue xsi:type="xs:string"
            x500:Encoding="LDAP">Steven</saml:AttributeValue>
    </saml:Attribute>


BASIC
_____


Two <Attribute> elements refer to the same SAML attribute if and only if the
values of their Name XML attributes are equal in the sense of Section 3.3.6 of
[Schema2].

No additional XML attributes are defined for use with the <Attribute> element.

The schema type of the contents of the <AttributeValue> element MUST be drawn
from one of the types defined in Section 3.3 of [Schema2]. The xsi:type
attribute MUST be present and be given the appropriate value.

X.500/LDAP Attribute Profile (URI)
__________________________________

**Extracted from the SAML2 core specifications**

Two <Attribute> elements refer to the same SAML attribute if and only if their
Name XML attribute values are equal in the sense of [RFC3061]. The
FriendlyName attribute plays no role in the comparison.

Directory attribute type definitions for use in native X.500 directories
specify the syntax of the attribute using ASN.1 [ASN.1]. For use in LDAP,
directory attribute definitions additionally include an LDAP syntax which
specifies how attribute or assertion values conforming to the syntax are to be
represented when transferred in the LDAP protocol (known as an LDAP-specific
encoding). The LDAP-specific encoding commonly produces Unicode characters in
UTF-8 form. This SAML attribute profile specifies the form of SAML attribute
values only for those directory attributes which have LDAP syntaxes. Future
extensions to this profile may define attribute value formats for directory
attributes whose syntaxes specify other encodings.

To represent the encoding rules in use for a particular attribute value, the
<AttributeValue> element MUST contain an XML attribute named Encoding defined
in the XML namespace urn:oasis:names:tc:SAML:2.0:profiles:attribute:X500.

For any directory attribute with a syntax whose LDAP-specific encoding
exclusively produces UTF-8 character strings as values, the SAML attribute
value is encoded as simply the UTF-8 string itself, as the content of the
<AttributeValue> element, with no additional whitespace.
In such cases, the xsi:type XML attribute MUST be set to xs:string.
The profile-specific Encoding XML attribute is provided, with a value of LDAP.

The AttributeData instances have a field expiration_data. It the profile
exists, obsolete data are removed at loading.


When authentic 2 deals with attributes and needs mapping?
---------------------------------------------------------

Authentic 2 behaves as an attribute provider:
* At the SSO login
* When an attribute request is received

Authentic requests (e.g. by soap) are not yet supported.

When Authentic 2 behaves as an attribute provider at SSO login
______________________________________________________________

At a SSO request, just before responding to the service provider, the saml2
idp module sends the signal 'add_attributes_to_response' giving the SP entity
ID.

The signal is connected to the function 'provide_attributes_at_sso()' in
charge of providing the attributes at the SSO for this SP.

**Attributes sources are of two kinds. The first ones are the sources that can
be requested by the IdP with a syncrhonous binding without user intercations.
These sources are called pull sources. They are for now limited to LDAP
sources. The other ones are sources are asyncrhonous bindings, usually
requiring user interactions. These sources are called push sources. They are
now limited to the attributes provided at SSO requests when the IdP acts as a
SAML2 SP. There attributes are put/found in the Django session.**

Each source in the system is declared with an instance of the AttributeSource
model. We'll see later that to forward attributes of push sources it is not
necessary that a source is declared in some circumstances.

To manage these sources an attribute policy is attached to services providers.
Then the service provider model must be extended with a attribute
attributes_at_sso_policy. The service provider must send the signal
'add_attributes_to_response'.

The implementation is actually done for SAML2 providers.

**In such a policy attributes from pull and push sources are treated
differently.**

**For pull sources, a list of attributes is indicated. Either an attribute is
searched in all the pull sources and whatever attribute value found is
returned. Or each attribute is indicated with a source. With each attribute is
indicated the output format and namespace.**

**The policy may also indicate that all the attributes in the Django session
must be forwarded. Then, no AttributeSource instance is required. All the
attributes are then forwarded without treating input namespace considerations.
When an AttributeSource instance is found, the input namespace of this source
is considered. An option can then be set to tell that the output format and
namespace must be taken. A list of attribute can also be given.
This list can be use to filter attributes to forward without or without taking
care of the source. The output namespace and format can also be trated per
attribute.**

If the namespace is default, the attribute names will be taken from the
system namespace. In BASIC the name will be the definition name. In URI, the
Name will be the OID in urn format and the friendly name will be the
definition name. If a namespace is given, the first identifier of this
attribute is taken as Name in BASIC. In URI, the same and the first friendly
name is taken.

::

    class LibertyServiceProvider(models.Model):
        ...
        attribute_policy = models.ForeignKey(AttributePolicy,
                verbose_name=_("Attribute policy"), null=True, blank=True)

    class AttributePolicy(models.Model):
        # List of attributes to provide from pull sources at SSO Login.
        # If an attribute is indicate without a source, from any source.
        # The output format and namespace is given by each attribute.
        attribute_list_for_sso_from_pull_sources = \
            models.ForeignKey(LibertyAttributeMap,
            related_name = "attributes of pull sources",
            blank = True, null = True)

        # Set to true for proxying attributes from pull sources at SSO Login.
        # Attributes are in session.
        # All attributes are forwarded as is except if the parameter
        # 'attribute_list_for_sso_from_push_sources' is initialized
        forward_attributes_from_pull_sources = models.BooleanField(default=False)

        # Map attributes in session
        # forward_attributes_in_session must be true
        # At False, all attributes are forwarded as is
        # At true, look for the namespace of the source for input, If not found,
        # system namespace. Look for the options attribute_name_format and
        # output_namespace of the attribute policy for output.
        map_attributes_from_pull_sources = models.BooleanField(default=False)

        # ATTRIBUTE_VALUE_FORMATS[0] =>
        #    (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC, 'SAMLv2 BASIC')
        output_name_format = models.CharField(max_length = 100,
            choices = ATTRIBUTE_VALUE_FORMATS,
            default = ATTRIBUTE_VALUE_FORMATS[0])

        #ATTRIBUTES_NS[0] => ('Default', 'Default')
        output_namespace = models.CharField(max_length = 100,
            choices = ATTRIBUTES_NS, default = ATTRIBUTES_NS[0])

        # Filter attributes pushed from source.
        source_filter_for_sso_from_push_sources = \
            models.ManyToManyField(AttributeSource,
            related_name = "attributes of pull sources",
            blank = True, null = True)

        # List of attributes to filter from pull sources at SSO Login.
        attribute_filter_for_sso_from_push_sources = \
            models.ForeignKey(LibertyAttributeMap,
            related_name = "attributes of pull sources",
            blank = True, null = True)

        # The sources of attributes of the previous list are considered.
        # May be used conjointly with 'source_filter_for_sso_from_push_sources'
        filter_source_of_filtered_attributes = models.BooleanField(default=False)

        # To map the attributes of forwarded attributes with the defaut output
        # format and namespace, use 'map_attributes_from_pull_sources'
        # Use the following option to use the output format and namespace
        # indicated for each attribute.
        map_attributes_of_filtered_attributes = models.BooleanField(default=False)


        # Set to true to take in account missing required attributes
        send_error_and_no_attrs_if_missing_required_attrs = \
            models.BooleanField(default=False)

        class Meta:
            verbose_name = _('attribute options policy')
            verbose_name_plural = _('attribute options policies')


    class AttributeList(models.Model):
        name = models.CharField(max_length = 40, unique = True)
        attributes = models.ManyToManyField(AttributeItem,
            related_name = "attributes of the list",
            blank = True, null = True)


    class AttributeItem(models.Model):
        attribute_name = models.CharField(max_length = 100, choices = ATTRIBUTES,
            default = ATTRIBUTES[0])
        # ATTRIBUTE_VALUE_FORMATS[0] =>
        #    (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC, 'SAMLv2 BASIC')
        output_attribute_name_format = models.CharField(max_length = 100,
            choices = ATTRIBUTE_VALUE_FORMATS,
            default = ATTRIBUTE_VALUE_FORMATS[0])
        #ATTRIBUTES_NS[0] => ('Default', 'Default')
        output_namespace = models.CharField(max_length = 100,
            choices = ATTRIBUTES_NS, default = ATTRIBUTES_NS[0])
        required = models.BooleanField(default=False)
        source = models.ForeignKey(AttributeSource, blank = True, null = True)


A list of attributes can also be taken from the service provider metadata and
added to 'attribute_list_for_sso_from_pull_sources'. The namespace may be
extracted from the metadata. This namespace is then used to look for the
corresponding definition and then to provide the attribute in the right
namespace. Read attributes from metadata is not yet supported.

For the attributes of pull sources, once the list of attributes is defined,
They are loaded in the user profile.

As explained before the attribute_aggregator loading function send signals to
grab dictionnary of attributes. Up to know, only the ldap loading function are
connected to these signals. The namespace of LDAP sources is assumed to be
the same as the system namespace. There is here then no mapping needed. Other
kind of sources than LDAP can be defined in attribute aggregator.

To grab attributes from a LDAP the user dn in the LDAP  or at least a local
identifier in the LDAP is required. For this purpose, each user has alias
associated with LDAP source. These aliases must their DN in the LDAP. When
the authentication LDAP backend will be taken in account, the dn will be taken
direclty from the user Model instance.

Each LDAP sources are declared with the binding parameters. The LDAP namespace
is always 'Default'.

If an attribute to load is not found and is required the answer should report
an error (Not yet implemented).

Attributes in response can also be provided with other means than from an LDAP
source. Attributes can be put in the user Django session and then loaded in
the profile. An option of the service provier indicate if attributes in the
session must be provided to the service provider.

To have the attribute loaded from the session, they must be provided in the
session as follows:
request.session['attributes'][source_name] = list()

The source_name must be the name of an existing instance of an
'AttributeSource'. Such an instance contains a field namespace indicating the
namespace of attributes.

This is currently implemented only for the SAML2 service provider module of
authentic2. Authsaml2, the SP module, parse the assertion and put the
attributes in the session.

Then, Authentic 2 can be used as a SAML2 proxy forwarding attributes in
assertion, eventually doing a namespace mapping. For this, the option
forward attributes in sesion must be set (by default False).
