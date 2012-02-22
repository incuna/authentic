'''
    VERIDIC Project - Towards a centralized access control system

    Copyright (C) 2011  Mikael Ates

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import time
import datetime
import logging
import re

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from authentic2.attribute_aggregator.xacml_constants import *
from authentic2.attribute_aggregator.mapping import ATTRIBUTE_MAPPING


logger = logging.getLogger('attribute_aggregator')


def iso8601_to_datetime(date_string):
    '''
        Convert a string formatted as an ISO8601 date into a time_t value.
        This function ignores the sub-second resolution.
    '''
    m = re.match(r'(\d+-\d+-\d+T\d+:\d+:\d+)(?:\.\d+)?Z?$', date_string)
    if not m:
        raise ValueError('Invalid ISO8601 date')
    tm = time.strptime(m.group(1)+'Z', "%Y-%m-%dT%H:%M:%SZ")
    return datetime.datetime.fromtimestamp(time.mktime(tm))


def get_all_attribute_definitions():
    return ATTRIBUTE_MAPPING.keys()


def get_all_sources():
    from authentic2.attribute_aggregator.models import AttributeSource
    return AttributeSource.objects.all()


def get_full_definition(definition):
    if not definition in ATTRIBUTE_MAPPING:
        return None
    return ATTRIBUTE_MAPPING[definition]


def get_def_name_from_oid(oid):
    if not oid:
        return None
    for def_name, content in ATTRIBUTE_MAPPING.items():
        if 'oid' in content:
            if content['oid'] == oid:
                return def_name
    return None


def get_oid_from_def_name(definition_name):
    if not definition_name or not definition_name in ATTRIBUTE_MAPPING \
            or not 'oid' in ATTRIBUTE_MAPPING[definition_name]:
        return None
    return ATTRIBUTE_MAPPING[definition_name]['oid']


def get_def_name_from_alias(alias):
    if not alias:
        return None
    for def_name, content in ATTRIBUTE_MAPPING.items():
        if 'alias' in content:
            if alias in content['alias']:
                return def_name
    return None


def get_definition_from_oid(oid):
    if not oid:
        return None
    for def_name, content in ATTRIBUTE_MAPPING.items():
        if 'oid' in content:
            if content['oid'] == oid:
                return ATTRIBUTE_MAPPING[def_name]
    return None


def get_definition_from_alias(alias):
    if not alias:
        return None
    for def_name, content in ATTRIBUTE_MAPPING.items():
        if 'alias' in content:
            if alias in content['alias']:
                return ATTRIBUTE_MAPPING[def_name]
    return None


def get_profile_field_name_from_definition(definition):
    if definition and definition in ATTRIBUTE_MAPPING \
            and 'profile_field_name' in ATTRIBUTE_MAPPING[definition]:
        return ATTRIBUTE_MAPPING[definition]['profile_field_name']
    return None


def get_definition_from_profile_field_name(field_name):
    if not field_name:
        return None
    for def_name, content in ATTRIBUTE_MAPPING.items():
        if 'profile_field_name' in content:
            if field_name == content['profile_field_name']:
                return def_name
    return None


def get_def_name_from_name_and_ns_of_attribute(name, namespace):
    if not name or not namespace:
        return None
    for def_name, content in ATTRIBUTE_MAPPING.items():
        if "namespaces" in content \
                and namespace in content["namespaces"].keys():
            if name in content["namespaces"][namespace]["identifiers"]:
                return def_name
            if name in content["namespaces"][namespace]["friendly_names"]:
                return def_name
    return None


def get_attribute_name_in_namespace(definition, namespace):
    if not definition or not namespace:
        return None
    logger.debug('get_attribute_name_in_namespace: look for %s in %s' \
        % (definition, namespace))
    if definition in ATTRIBUTE_MAPPING:
        logger.debug('get_attribute_name_in_namespace: definition found')
        if "namespaces" in ATTRIBUTE_MAPPING[definition]\
                and namespace in ATTRIBUTE_MAPPING[definition]["namespaces"]:
            logger.debug('get_attribute_name_in_namespace: namespace found')
            return ATTRIBUTE_MAPPING[definition]\
                ["namespaces"][namespace]["identifiers"][0]
    return None


def get_attribute_friendly_name_in_namespace(definition, namespace):
    if not definition or not namespace:
        return None
    if definition in ATTRIBUTE_MAPPING:
        if "namespaces" in ATTRIBUTE_MAPPING[definition]\
                and namespace in ATTRIBUTE_MAPPING[definition]["namespaces"]:
            return ATTRIBUTE_MAPPING[definition]\
                ["namespaces"][namespace]["friendly_names"][0]
    return None


def get_attribute_type_of_definition(definition):
    if not definition or not definition in ATTRIBUTE_MAPPING \
            or not 'type' in ATTRIBUTE_MAPPING[definition]:
        return None
    return ATTRIBUTE_MAPPING[definition]["type"]


def is_alias_of_definition(definition_name, alias):
    if definition_name in ATTRIBUTE_MAPPING \
            and 'alias' in ATTRIBUTE_MAPPING[definition_name] \
            and alias in ATTRIBUTE_MAPPING[definition_name]['alias']:
        return True
    return False


def is_oid_of_definition(definition_name, oid):
    if definition_name in ATTRIBUTE_MAPPING \
            and 'oid' in ATTRIBUTE_MAPPING[definition_name] \
            and oid == ATTRIBUTE_MAPPING[definition_name]['oid']:
        return True
    return False


def convert_from_string(definition_name, value):
    if not definition_name in ATTRIBUTE_MAPPING:
        return None
    type_ = ATTRIBUTE_MAPPING[definition_name]['type']

    if type_ == ACS_XACML_DATATYPE_STRING:
        return value
    elif type_ == ACS_XACML_DATATYPE_BOOLEAN:
        if value in ('True', 'true', 'Vrai', 'vrai'):
            return True
        return False
    elif type_ == ACS_XACML_DATATYPE_INTEGER:
        try:
            return int(value)
        except:
            return None
    elif type_ == ACS_XACML_DATATYPE_DOUBLE:
        try:
            return float(value)
        except:
            return None
    elif type_ == ACS_XACML_DATATYPE_TIME:
        try:
            return time.strptime(value, "%h:%m:%s") #12:15:00
        except:
            return None
    elif type_ == ACS_XACML_DATATYPE_DATE:
        try:
            return time.strptime(value, "%d/%b/%Y") #28/01/1982
        except:
            return None
    elif type_ == ACS_XACML_DATATYPE_DATETIME:
        try:
            return iso8601_to_datetime(value)
        except:
            return None
    elif type_ == ACS_XACML_DATATYPE_RFC822NAME: # email
        r = re.compile(\
            '[a-zA-Z0-9+_\-\.]+@[0-9a-zA-Z][.-0-9a-zA-Z]*.[a-zA-Z]+')
        if r.search(value):
            return value
        else:
            return None
    elif type_ == ACS_XACML_DATATYPE_IPADDRESS: # x.x.x.x
        r = re.compile(\
            '(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})')
        if r.search(value):
            return value
        else:
            return None
    return None


@transaction.commit_manually
def load_or_create_user_profile(user=None, no_cleanup=False):
    '''
        If the user has a profile, remove assertions outdated and return
        profile, else create a new one.

        If cleanup: expiration_date < now() remove assertion data from profile

        If no_cleanup: return profile if any without removing outdated
        assertions
    '''
    from authentic2.attribute_aggregator.models import UserAttributeProfile
    profile = None
    try:
        if user:
            try:
                logger.debug('load_or_create_user_profile: \
                    search profile for %s' \
                    % user)
                profile = UserAttributeProfile.objects.get(user=user)
            except ObjectDoesNotExist:
                try:
                    profile = UserAttributeProfile(user=user)
                    profile.save()
                    logger.info('load_or_create_user_profile: \
                        profile with id %s for user %s created' \
                        % (str(profile.id), user))
                except:
                    profile = UserAttributeProfile()
                    profile.save()
                    logger.debug('load_or_create_user_profile: \
                        profile with id %s for an anonymous user created' \
                        % str(profile.id))
            else:
                if no_cleanup:
                    logger.debug('load_or_create_user_profile: Existing user \
                        profile %s for %s - No cleanup' % (profile, user))
                else:
                    profile.cleanup()
                    profile.save()
        elif not user:
            profile = UserAttributeProfile()
            profile.save()
            logger.debug('load_or_create_user_profile: \
                profile with id %s for an anonymous user created' \
                % str(profile.id))
    except Exception, err:
        transaction.rollback()
        logger.error('load_or_create_user_profile: An error occured %s' \
            % str(err))
        return None
    else:
        transaction.commit()
        logger.debug('load_or_create_user_profile: everything successfully \
            performed')
        return profile


def get_user_alias_in_source(user, source):
    from authentic2.attribute_aggregator.models import UserAliasInSource
    try:
        alias = UserAliasInSource.objects.get(user=user, source=source)
        return alias.name
    except:
        return None


def set_user_alias_in_source(user, source, name, force_change=False):
    from authentic2.attribute_aggregator.models import UserAliasInSource
    logger.debug('set_user_alias_in_source: set alias %s for user %s in \
        source %s' % (name, user, source))
    alias = None
    try:
        '''
            If this user has already an alias, we change it.
        '''
        alias = UserAliasInSource.objects.get(user=user, source=source)
        logger.warn('set_user_alias_in_source: \
            this user has already an alias, we change it.')
        alias.delete()
    except:
        pass
    try:
        '''
            If a user has already this alias...
            force_change: we give it to this user
        '''
        alias = UserAliasInSource.objects.get(name=name, source=source)
        if not force_change:
            logger.warn('set_user_alias_in_source: \
                a user has already this alias, we do nothing.')
            return None
        logger.warn('set_user_alias_in_source: \
            a user has already this alias, we give it to %s.' % user)
        alias.delete()
    except:
        pass
    try:
        alias = UserAliasInSource(user=user, name=name, source=source)
        alias.save()
        logger.debug('set_user_alias_in_source: alias created.')
        return alias
    except Exception, err:
        logger.error('set_user_alias_in_source: unable to create alias due \
            to %s.' % str(err))
        return None
