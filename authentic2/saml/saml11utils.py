import xml.etree.ElementTree as etree
import lasso
from authentic2.saml import x509utils
from authentic2.saml.saml2utils import bool2xs, NamespacedTreeBuilder, keyinfo

class Saml11Metadata(object):
    ENTITY_DESCRIPTOR = 'EntityDescriptor'
    SP_SSO_DESCRIPTOR = 'SPDescriptor'
    IDP_SSO_DESCRIPTOR = 'IDPDescriptor'
    PROTOCOL_SUPPORT_ENUMERATION = 'protocolSupportEnumeration'
    SOAP_ENDPOINT = 'SoapEndpoint'
    PROVIDER_ID = 'providerID'
    VALID_UNTIL = 'validUntil'
    CACHE_DURATION = 'cacheDuration'
    ENCRYPTION_METHOD = 'EncryptionMethod'
    KEY_SIZE = 'KeySize'
    KEY_DESCRIPTOR = 'KeyDescriptor'
    SERVICE_URL = "ServiceURL"
    SERVICE_RETURN_URL = "ServiceReturnURL"
    USE = 'use'
    PROTOCOL_PROFILE = 'ProtocolProfile'
    FEDERATION_TERMINATION_NOTIFICATION_PROTOCOL_PROFILE = \
        'FederationTerminationNotificationProtocolProfile'
    AUTHN_REQUESTS_SIGNED = 'AuthnRequestsSigned'
    # Service prefixes
    SINGLE_LOGOUT = 'SingleLogout'
    FEDERATION_TERMINATION = 'FederationTermination'
    REGISTER_NAME_IDENTIFIER = 'RegisterNameIdentifier'
    # SP Services prefixes
    ASSERTION_CONSUMER = 'AssertionConsumer'
    # IDP Services prefixes
    SINGLE_SIGN_ON = 'SingleSignOn'
    AUTHN = 'Authn'

    sso_services = ( SOAP_ENDPOINT, SINGLE_LOGOUT, FEDERATION_TERMINATION,
            REGISTER_NAME_IDENTIFIER )
    idp_services = ( SINGLE_SIGN_ON, AUTHN)
    sp_services = ( ASSERTION_CONSUMER, AUTHN_REQUESTS_SIGNED)

    def __init__(self, entity_id, url_prefix = '', valid_until = None,
            cache_duration = None, protocol_support_enumeration = []):
        '''Initialize a new generator for a metadata file.

           Entity id is the name of the provider
        '''
        self.entity_id = entity_id
        self.url_prefix = url_prefix
        self.role_descriptors = {}
        self.valid_until = valid_until
        self.cache_duration = cache_duration
        self.tb = NamespacedTreeBuilder()
        self.tb.pushNamespace(lasso.METADATA_HREF)
        if not protocol_support_enumeration:
            raise TypeError('Protocol Support Enumeration is mandatory')
        self.protocol_support_enumeration = protocol_support_enumeration

    def add_role_descriptor(self, role, map, options):
        '''Add a role descriptor, map is a sequence of tuples formatted as

              (endpoint_type, (bindings, ..) , url [, return_url])'''
        if not self.SOAP_ENDPOINT in map:
            raise TypeError('SoapEndpoint is mandatory in SAML 1.1 role descriptors')
        self.role_descriptors[role] = (map, options)

    def add_sp_descriptor(self, map, options):
        if not self.ASSERTION_CONSUMER in map:
            raise TypeError('AssertionConsumer is mandarotyr in SAML 1.1 SP role descriptors')
        for row in map:
            if row not in self.sp_services + self.sso_services:
                raise TypeError(row)
        self.add_role_descriptor('sp', map, options)

    def add_idp_descriptor(self, map, options):
        if not self.SINGLE_SIGN_ON in map:
            raise TypeError('SingleSignOn is mandarotyr in SAML 1.1 SP role descriptors')
        for row in map:
            if row not in self.idp_services + self.sso_services:
                raise TypeError(row)
        self.add_role_descriptor('idp', map, options)

    def add_keyinfo(self, key, use, encryption_method = None, key_size = None):
        attrib = {}
        if use:
            attrib = { self.USE: use }
        self.tb.start(self.KEY_DESCRIPTOR, attrib)
        if encryption_method:
            self.tb.simple_content(self.ENCRYPTION_METHOD, encryption_method)
        if key_size:
            self.tb.simple_content(self.KEY_SIZE, str(key_size))
        keyinfo(self.tb, key)
        self.tb.end(self.KEY_DESCRIPTOR)

    def add_service_url(self, name, map):
        service = map.get(name)
        if service:
            service_urls = service[0]
            self.tb.simple_content(name + self.SERVICE_URL,
                self.url_prefix + service_urls[0])
            if len(service_urls) == 2:
                self.tb.simple_content(name + self.SERVICE_RETURN_URL,
                    self.url_prefix + service_urls[1])

    def add_profile(self, name, map, tag = None):
        if not tag:
            tag = name + self.PROTOCOL_PROFILE
        service = map.get(name)
        if service:
            service_profiles = service[1]
            for profile in service_profiles:
                self.tb.simple_content(tag, profile)

    def generate_sso_descriptor(self, name, map, options):
        attrib = {}

        if options.get('valid_until'):
            attrib[self.VALID_UNTIL] = options['valid_until']
        if options.get('cached_duration'):
            attrib[self.CACHE_DURATION] = options['cache_duration']
        attrib[self.PROTOCOL_SUPPORT_ENUMERATION] = options[self.PROTOCOL_SUPPORT_ENUMERATION]
        self.tb.start(name, attrib)
        # Add KeyDescriptor(s)
        if options.get('signing_key'):
            self.add_keyinfo(options['signing_key'], 'signing',)
        if options.get('encryption_key'):
            self.add_keyinfo(options['encryption_key'], 'encryption',
                    encryption_method = options.get('encryption_method'),
                    key_size = options.get('key_size'))
        if options.get('key'):
            self.add_keyinfo(options['encryption_key'], 'signing encryption',
                    encryption_method = options.get('encryption_method'),
                    key_size = options.get('key_size'))
        # Add SOAP Endpoint
        self.tb.simple_content(self.SOAP_ENDPOINT,
                self.url_prefix + map[self.SOAP_ENDPOINT])
        # Add SingleLogoutService
        self.add_service_url(self.SINGLE_LOGOUT, map)
        # Add FederationTerminationService URL
        self.add_service_url(self.FEDERATION_TERMINATION, map)
        self.add_profile(self.FEDERATION_TERMINATION, map,
             tag = self.FEDERATION_TERMINATION_NOTIFICATION_PROTOCOL_PROFILE)
        # Add SingleLogoutProtocolProfile
        self.add_profile(self.SINGLE_LOGOUT, map)
        # Add RegisterNameIdentifier
        self.add_profile(self.REGISTER_NAME_IDENTIFIER, map)
        self.add_service_url(self.REGISTER_NAME_IDENTIFIER, map)

    def generate_idp_descriptor(self, map, options):
        self.generate_sso_descriptor(self.IDP_SSO_DESCRIPTOR, map, options)
        # Add SingleSignOnServiceURL
        self.add_service_url(self.SINGLE_SIGN_ON, map)
        self.add_profile(self.SINGLE_SIGN_ON, map)
        # Add AuthnServiceURL
        self.add_service_url(self.AUTHN, map)
        self.tb.end(self.IDP_SSO_DESCRIPTOR)

    def generate_sp_descriptor(self, map, options):
        self.generate_sso_descriptor(self.SP_SSO_DESCRIPTOR, map, options)
        # Add AssertionConsumerServiceURL
        self.add_service_url(self.ASSERTION_CONSUMER)
        self.simple_content(self.AUTHN_REQUESTS_SIGNED,
                bool2xs(options.get(self.AUTHN_REQUESTS_SIGNED, False)))
        self.tb.end(self.SP_SSO_DESCRIPTOR)

    def root_element(self):
        attrib = { self.PROVIDER_ID : self.entity_id}
        if self.cache_duration:
            attrib['cacheDuration'] = self.cache_duration
        if self.valid_until:
            attrib['validUntil'] = self.valid_until
        self.entity_descriptor = self.tb.start(self.ENTITY_DESCRIPTOR, attrib)
        # Generate sso descriptor
        attrib =  { self.PROTOCOL_SUPPORT_ENUMERATION: ' '.join(self.protocol_support_enumeration) }
        if self.role_descriptors.get('idp'):
            map, options = self.role_descriptors['idp']
            options.update(attrib)
            self.generate_idp_descriptor(map, options)
        if self.role_descriptors.get('sp'):
            map, options = self.role_descriptors['sp']
            options.update(attrib)
            self.generate_idp_sso_descriptor(map, options)
        self.tb.end(self.ENTITY_DESCRIPTOR)
        return self.tb.close()

    def __str__(self):
        return '<?xml version="1.0"?>\n' + etree.tostring(self.root_element())

if __name__ == '__main__':
    pkey, _ = x509utils.generate_rsa_keypair()
    meta = Saml11Metadata('http://example.com/saml',
            'http://example.com/saml/prefix/',
            protocol_support_enumeration = [ lasso.LIB_HREF ])
    sso_protocol_profiles = [
        lasso.LIB_PROTOCOL_PROFILE_BRWS_ART,
        lasso.LIB_PROTOCOL_PROFILE_BRWS_POST,
        lasso.LIB_PROTOCOL_PROFILE_BRWS_LECP ]
    slo_protocol_profiles = [
        lasso.LIB_PROTOCOL_PROFILE_SLO_SP_HTTP,
        lasso.LIB_PROTOCOL_PROFILE_SLO_SP_SOAP,
        lasso.LIB_PROTOCOL_PROFILE_SLO_IDP_HTTP,
        lasso.LIB_PROTOCOL_PROFILE_SLO_IDP_SOAP ]
    options = { 'signing_key': pkey }
    meta.add_idp_descriptor({
            'SoapEndpoint': 'soap',
            'SingleLogout': (('slo', 'sloReturn'), slo_protocol_profiles),
            'SingleSignOn': (('sso',), sso_protocol_profiles),
        }, options)
    root = meta.root_element()
    print etree.tostring(root)
