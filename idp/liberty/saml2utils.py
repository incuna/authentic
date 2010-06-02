import xml.etree.ElementTree as etree
import lasso
import x509utils
import base64
import binascii

def bool2xs(boolean):
    '''Convert a boolean value to XSchema boolean representation'''
    if boolean is True:
        return 'true'
    if boolean is False:
        return 'false'
    raise TypeError()

class NamespacedTreeBuilder(etree.TreeBuilder):
    def __init__(self, *args, **kwargs):
        self.__old_ns = []
        self.__ns = None
        return etree.TreeBuilder.__init__(self, *args, **kwargs)

    def pushNamespace(self, ns):
        self.__old_ns.append(self.__ns)
        self.__ns = ns

    def popNamespace(self):
        self.__ns = self.__old_ns.pop()

    def start(self, tag, attrib):
        return etree.TreeBuilder.start(self, '{%s}%s' % (self.__ns, tag), attrib)

    def end(self, tag):
        return etree.TreeBuilder.end(self, '{%s}%s' % (self.__ns, tag))

class Saml2Metadata(NamespacedTreeBuilder):
    ENTITY_DESCRIPTOR = 'EntityDescriptor'
    SP_SSO_DESCRIPTOR = 'SPSSODescriptor'
    IDP_SSO_DESCRIPTOR = 'IDPSSODescriptor'
    ARTIFACT_RESOLUTION_SERVICE = 'ArtifactResolutionService'
    SINGLE_LOGOUT_SERVICE = 'SingleLogoutService'
    MANAGE_NAME_ID_SERVICE = 'ManageNameIDService'
    SINGLE_SIGN_ON_SERVICE = 'SingleSignOnService'
    NAME_ID_MAPPING_SERVICE = 'NameIDMappingService'
    ASSERTION_ID_REQUEST_SERVICE = 'AssertionIDRequestService'
    ASSERTION_CONSUMER_SERVICE = 'AssertionConsumerService'
    PROTOCOL_SUPPORT_ENUMERATION = 'protocolSupportEnumeration'
    KEY_DESCRIPTOR = 'KeyDescriptor'

    sso_services = ( ARTIFACT_RESOLUTION_SERVICE, SINGLE_LOGOUT_SERVICE,
            MANAGE_NAME_ID_SERVICE )
    idp_services = ( SINGLE_SIGN_ON_SERVICE, NAME_ID_MAPPING_SERVICE,
            ASSERTION_ID_REQUEST_SERVICE )
    sp_services = ( ASSERTION_CONSUMER_SERVICE, )

    def __init__(self, entity_id, url_prefix = '', valid_until = None,
            cache_duration = None):
        '''Initialize a new generator for a metadata file.

           Entity id is the name of the provider
        '''
        self.entity_id = entity_id
        self.url_prefix = url_prefix
        self.role_descriptors = {}
        self.valid_until = valid_until
        self.cache_duration = cache_duration
        self.tb = NamespacedTreeBuilder()
        self.tb.pushNamespace(lasso.SAML2_METADATA_HREF)

    def add_role_descriptor(self, role, map, options):
        '''Add a role descriptor, map is a sequence of tuples formatted as

              (endpoint_type, (bindings, ..) , url [, return_url])
           
           endpoint_type is a string among:

              - SingleSignOnService
              - AssertionConsumer
              - SingleLogoutService
              - ManageNameIDService
              - AuthzService
              - AuthnQueryService
              - AttributeService
              - AssertionIDRequestService'''
        self.role_descriptors[role] = (map, options)

    def add_sp_descriptor(self, map, options):
        for row in map:
            if row[0] not in self.sp_services + self.sso_services:
                raise TypeError()
        self.add_role_descriptor('sp', map, options)

    def add_idp_descriptor(self, map, options):
        for row in map:
            if row[0] not in self.idp_services + self.sso_services:
                raise TypeError()
        self.add_role_descriptor('idp', map, options)

    def generate_services(self, map, options, listing):
        if options:
            if 'NameIDFormat' in options:
                for name_id_format in options['NameIDFormat']:
                    self.tb.start('NameIDFormat', {})
                    self.tb.data(name_id_format)
                    self.tb.end('NameIDFormat')
            if 'cache_duration' in options:
                attrib['cacheDuration'] = options['cache_duration']
            if 'valid_until' in options:
                attrib['validUntil'] = options['valid_until']
            if 'error_url' in options:
                attrib['errorURL'] = options['error_url']
            if 'signing_key' in options:
                self.add_keyinfo(options['signing_key'], 'signing')
            if 'encryption_key' in options:
                self.add_keyinfo(options['encryption_key'], 'signing')
            if 'key' in options:
                self.add_keyinfo(options['key'], 'signing encryption')
        assertion_consumer_idx = 1
        for service in listing:
            selected = [ row for row in map if row[0] == service ]
            for row in selected:
                if isinstance(row[1], str):
                    bindings = [ row[1] ]
                else:
                    bindings = row[1]
                for binding in bindings:
                    attribs = { 'Binding' : binding,
                            'Location': self.url_prefix + row[2] }
                    if len(row) == 4:
                        attribs['ResponseLocation'] = self.url_prefix + row[3]
                    if service == self.ASSERTION_CONSUMER_SERVICE:
                        attribs['index'] = str(assertion_consumer_idx)
                        assertion_consumer_idx += 1
                    self.tb.start(service, attribs)
                    self.tb.end(service)


    def add_keyinfo(self, key, use):
        def int_to_b64(i):
            h = hex(i)[2:].strip('L')
            if len(h) % 2 == 1:
                h = '0' + h
            return base64.b64encode(binascii.unhexlify(h))
        attrib = {}
        if use:
            attrib = { 'use': use }
        self.tb.start(self.KEY_DESCRIPTOR, attrib)
        self.tb.pushNamespace(lasso.DS_HREF)
        self.tb.start('KeyInfo', {})
        if 'CERTIF' in key:
            naked = x509utils.decapsulate_pem_file(key)
            self.tb.start('X509Data', {})
            self.tb.start('X509Certificate', {})
            self.tb.data(naked)
            self.tb.end('X509Certificate', {})
            self.tb.end('X509Data', {})
        else:
            self.tb.start('KeyValue', {})
            self.tb.start('RSAKeyValue', {})
            self.tb.start('Modulus', {})
            self.tb.data(int_to_b64(x509utils.get_rsa_public_key_modulus(key)))
            self.tb.end('Modulus')
            self.tb.start('Exponent', {})
            self.tb.data(int_to_b64(x509utils.get_rsa_public_key_exponent(key)))
            self.tb.end('Exponent')
            self.tb.end('RSAKeyValue')
            self.tb.end('KeyValue')
        self.tb.end('KeyInfo')
        self.tb.popNamespace()
        self.tb.end(self.KEY_DESCRIPTOR)

    def root_element(self):
        attrib = { 'entityID' : self.entity_id}
        if self.cache_duration:
            attrib['cacheDuration'] = self.cache_duration
        if self.valid_until:
            attrib['validUntil'] = self.valid_until

        self.entity_descriptor = self.tb.start(self.ENTITY_DESCRIPTOR, attrib)
        # Generate sso descriptor
        attrib =  { self.PROTOCOL_SUPPORT_ENUMERATION: lasso.SAML2_PROTOCOL_HREF }
        if self.role_descriptors.get('sp'):
            map, options = self.role_descriptors['sp']
            self.sp_descriptor = self.tb.start(self.SP_SSO_DESCRIPTOR, attrib)
            self.generate_services(map, options, self.sso_services)
            self.generate_services(map, {}, self.sp_services)
            self.tb.end(self.SP_SSO_DESCRIPTOR)
        if self.role_descriptors.get('idp'):
            map, options = self.role_descriptors['idp']
            self.sp_descriptor = self.tb.start(self.IDP_SSO_DESCRIPTOR, attrib)
            self.generate_services(map, options, self.sso_services)
            self.generate_services(map, {}, self.idp_services)
            self.tb.end(self.IDP_SSO_DESCRIPTOR)
        self.tb.end(self.ENTITY_DESCRIPTOR)
        return self.tb.close()

    def __str__(self):
        return '<?xml version="1.0"?>\n' + etree.tostring(self.root_element())

if __name__ == '__main__':
    pkey, _ = x509utils.generate_rsa_keypair()
    meta = Saml2Metadata('http://example.com/saml', 'http://example.com/saml/prefix/')
    meta.add_sp_descriptor((
        ('SingleLogoutService', lasso.SAML2_METADATA_BINDING_SOAP, 'logout', 'logoutReturn' ),
        ('ManageNameIDService', [ lasso.SAML2_METADATA_BINDING_SOAP, lasso.SAML2_METADATA_BINDING_REDIRECT, lasso.SAML2_METADATA_BINDING_POST ], 'manageNameID', 'manageNameIDReturn' ), 
        ('AssertionConsumerService', [ lasso.SAML2_METADATA_BINDING_POST ], 'acs'),), {'signing_key': pkey})
    root = meta.root_element()
    print etree.tostring(root)
