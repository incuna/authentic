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
ENTITY_ID = 'entityID'

def load_one_entity(tree, options):
    '''Load or update an EntityDescriptor into the database'''
    entity_id = tree.get(ENTITY_ID)
    organization_display_name = tree.find(ORGANIZATION_DISPLAY_NAME)
    organization_name = tree.find(ORGANIZATION_NAME)
    org = organization_display_name or organization_name
    if org:
        name = org.text
    else:
        name = entity_id
    idp, sp = False, False
    idp = len(tree.findall(IDP_SSO_DESCRIPTOR_TN)) != 0
    sp = len(tree.findall(SP_SSO_DESCRIPTOR_TN)) != 0
    if options.get('idp'):
        sp = False
    if options.get('sp'):
        idp = False
    if idp or sp:
        if options.get('delete'):
            LibertyProvider.objects.filter(entity_id=entity_id).delete()
            print 'Deleted', entity_id
            return
        if options['verbosity'] == '2':
            print >>sys.stdout, 'Loading %s, %s', %(name, entity_id)
        provider, created = LibertyProvider.objects.get_or_create(entity_id=entity_id,
                protocol_conformance=3)
        provider.name = name
        provider.metadata = etree.tostring(tree, encoding='utf-8').decode('utf-8')
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
