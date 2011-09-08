from optparse import make_option
import sys
import xml.etree.ElementTree as etree

import lasso
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

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
    default_name_id_format = options['sp_default_nameid_format']
    if default_name_id_format not in NAME_ID_FORMATS:
        default_name_id_format = 'transient'
    accepted_name_id_format = map(str.strip, options['sp_accepted_nameid_format'].split(','))
    accepted_name_id_format = filter(lambda x: x in NAME_ID_FORMATS, accepted_name_id_format)
    if not accepted_name_id_format:
        accepted_name_id_format = 'transient,persistent,email'.split(',')
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
        provider, created = LibertyProvider.objects.get_or_create(entity_id=entity_id,
                protocol_conformance=3)
        if options['verbosity'] == '2':
            if created:
                what = 'Creating'
            else:
                what = 'Updating'
            print '%(what)s %(name)s, %(id)s' % { 'what': what,
                    'name': name.encode('utf8'), 'id': entity_id}
        provider.name = name
        provider.metadata = etree.tostring(tree, encoding='utf-8').decode('utf-8').strip()
        provider.protocol_conformance = 3
        provider.federation_source = options['source']
        provider.save()
        options['count'] = options.get('count', 0) + 1
        if idp:
            identity_provider, created = LibertyIdentityProvider.objects.get_or_create(
                    liberty_provider=provider)
            identity_provider.enabled = True
            identity_provider.allow_create = True
            identity_provider.save()
        if sp:
            service_provider, created = LibertyServiceProvider.objects.get_or_create(
                    liberty_provider=provider)
            service_provider.enabled = True
            service_provider.default_name_id_format = default_name_id_format
            service_provider.accepted_name_id_format = accepted_name_id_format
            service_provider.save()

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
        make_option('--sp-default-nameid-format',
            dest='sp_default_nameid_format',
            default='transient',
            help='Default NameID format to return to a service provider'),
        make_option('--sp-accepted-nameid-format',
            dest='sp_accepted_nameid_format',
            default='persistent,transient,email',
            help='NameID format accepted for a service provider'),
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
        make_option('--source',
            dest='source',
            default=None,
            help='Tag the loaded providers with the given source string, \
existing providers with the same tag will be removed if they do not exist\
 anymore in the metadata file.'),
        )
    args = '<metadata_file>'
    help = 'Load the specified SAMLv2 metadata file'

    @transaction.commit_manually
    def handle(self, *args, **options):
        source = options['source']
        try:
            if not args:
                raise CommandError('No metadata file on the command line')
            # Check sources
            try:
                if source is not None:
                    source.decode('ascii')
            except:
                raise CommandError('--source MUST be an ASCII string value')
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
                loaded = []
                for entity_descriptor in doc.getroot().findall(ENTITY_DESCRIPTOR_TN):
                    try:
                        load_one_entity(entity_descriptor, options)
                        loaded.append(entity_descriptor.get(ENTITY_ID))
                    except Exception, e:
                        raise
                        entity_id = entity_descriptor.get(ENTITY_ID)
                        if options['ignore-errors']:
                            print >>sys.stderr, 'Unable to load EntityDescriptor for %s: %s' % (entity_id, str(e))
                        else:
                            raise CommandError('EntityDescriptor loading: %s' % str(e))
                if options['source']:
                    if options['delete']:
                        print 'Finally delete all providers for source: %s...' % source
                        LibertyProvider.objects.filter(federation_source=source).delete()
                    else:
                        to_delete = LibertyProvider.objects.filter(federation_source=source)\
                                .exclude(entity_id__in=loaded)
                        for provider in to_delete:
                            print 'Delete obsolete provider %s' % provider.entity_id
                            provider.delete()
            else:
                raise CommandError('%s is not a SAMLv2 metadata file' % metadata_file)
        except:
            transaction.rollback()
            raise
        else:
            transaction.commit()
        if not options.get('delete'):
            print 'Loaded', options.get('count', 0), 'providers'
