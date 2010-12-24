from optparse import make_option
import sys
import xml.etree.ElementTree as etree

import lasso
from django.core.management.base import BaseCommand, CommandError

from authentic2.saml.models import *


def md_element_name(tag_name):
    return '{%s}%s' % (lasso.SAML2_METADATA_HREF, tag_name)

ENTITY_DESCRIPTOR_TN = md_element_name('EntityDescriptor')
ENTITIES_DESCRIPTOR_TN = md_element_name('EntitiesDescriptor')
IDP_SSO_DESCRIPTOR_TN = md_element_name('IDPSSODescriptor')
SP_SSO_DESCRIPTOR_TN = md_element_name('SPSSODescriptor')
ORGANIZATION_DISPLAY_NAME = md_element_name('OrganizationDisplayName')
ORGANIZATION_NAME = md_element_name('OrganizationName')
ORGANIZATION = md_element_name('Organization')
ENTITY_ID = 'entityID'
PROTOCOL_SUPPORT_ENUMERATION = 'protocolSupportEnumeration'

def check_support_saml2(tree):
    if tree is not None and lasso.SAML2_PROTOCOL_HREF in tree.get(PROTOCOL_SUPPORT_ENUMERATION):
        return True
    return False

def load_one_entity(tree, options):
    '''Load or update an EntityDescriptor into the database'''
    entity_id = tree.get(ENTITY_ID)
    organization = tree.find(ORGANIZATION)
    name, org = None, None
    if organization:
        organization_display_name = organization.find(ORGANIZATION_DISPLAY_NAME)
        organization_name = organization.find(ORGANIZATION_NAME)
        org = organization_display_name or organization_name
        if org is not None:
            name = org.text
    if not name:
        name = entity_id
    idp, sp = False, False
    idp = check_support_saml2(tree.find(IDP_SSO_DESCRIPTOR_TN))
    sp = check_support_saml2(tree.find(SP_SSO_DESCRIPTOR_TN))
    if options.get('idp'):
        sp = False
    if options.get('sp'):
        idp = False
    if options.get('delete'):
        LibertyProvider.objects.filter(entity_id=entity_id).delete()
        print 'Deleted', entity_id
        return
    if idp or sp:
        if options['verbosity'] == '2':
            print >>sys.stdout, 'Loading %s, %s' % (name.encode('utf8'), entity_id)
        provider, created = LibertyProvider.objects.get_or_create(entity_id=entity_id,
                protocol_conformance=3)
        provider.name = name
        provider.metadata = etree.tostring(tree, encoding='utf-8').decode('utf-8').strip()
        provider.protocol_conformance = 3
        provider.save()
        options['count'] = options.get('count', 0) + 1
        if idp:
            identity_provider = LibertyIdentityProvider(liberty_provider=provider,
                enabled=True, allow_create=True)
            identity_provider.save()
        if sp:
            identity_provider = LibertyServiceProvider(liberty_provider=provider,
                enabled=True)
            identity_provider.save()

class Command(BaseCommand):
    '''Load SAMLv2 metadata file into the LibertyProvider, LibertyServiceProvider
    and LibertyIdentityProvider files'''
    can_import_django_settings = True
    output_transaction = True
    requires_model_validation = True
    option_list = BaseCommand.option_list + (
        make_option('--idp',
            action='store_true',
            dest='idp',
            default=False,
            help='Load identity providers only'),
        make_option('--sp',
            action='store_true',
            dest='sp',
            default=False,
            help='Load service providers only'),
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete all providers defined in the metadata file (kind of uninstall)'),
        make_option('--ignore-errors',
            action='store_true',
            dest='ignore-errors',
            default=False,
            help='If loading of one EntityDescriptor fails, continue loading'),
        )
    args = '<metadata_file>'
    help = 'Load the specified SAMLv2 metadata file'

    def handle(self, *args, **options):
        if not sys.argv:
            raise CommandError('No metadata file on the command line')
        try:
            metadata_file = file(args[0])
        except:
            raise CommandError('Unable to open file %s' % args[0])
        try:
            doc = etree.parse(metadata_file)
        except Exception, e:
            raise CommandError('XML parsing error: %s' % str(e))
        if doc.getroot().tag == ENTITY_DESCRIPTOR_TN:
            load_one_entity(doc.getroot(), options)
        elif doc.getroot().tag == ENTITIES_DESCRIPTOR_TN:
            for entity_descriptor in doc.getroot().findall(ENTITY_DESCRIPTOR_TN):
                try:
                    load_one_entity(entity_descriptor, options)
                except Exception, e:
                    entity_id = entity_descriptor.get(ENTITY_ID)
                    if options['ignore-errors']:
                        print >>sys.stderr, 'Unable to load EntityDescriptor for %s: %s' % (entity_id, str(e))
                    else:
                        raise
                        raise CommandError('EntityDescriptor loading: %s' % str(e))
        else:
            raise CommandError('%s is not a SAMLv2 metadata file' % metadata_file)
        if not options.get('delete'):
            print 'Loaded', options.get('count', 0), 'providers'
