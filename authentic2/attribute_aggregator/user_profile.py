'''
    VERIDIC - Towards a centralized access control system

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


import logging

from django.contrib.auth.models import SiteProfileNotAvailable
from django.core.exceptions import ObjectDoesNotExist

from core import get_profile_field_name_from_definition, \
    get_definition_from_profile_field_name


logger = logging.getLogger('attribute_aggregator.user_profile')


SOURCE_NAME = 'USER_PROFILE'

def get_attributes(user, definitions=None, source=None, **kwargs):
    '''
        Return attributes dictionnary

        Dictionnary format:
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
        a1['values'] = list_of_values
        data_from_source.append(a1)
        ...
        data_from_source.append(a2)
        attributes[source_name] = data_from_source

        First attempt on 'definition' key.
        Else, definition is searched by 'name' and 'namespece' keys.
    '''
    from models import AttributeSource
    try:
        AttributeSource.objects.get(name=SOURCE_NAME)
    except:
        logger.debug('get_attributes: \
            Profile source not configured')
        return None
    if source and source.name != SOURCE_NAME:
        logger.debug('get_attributes: \
            The required source %s is not user profile' % source)
        return None

    attributes = dict()
    data = []
    try:
        user_profile = user.get_profile()
        fields = []
        if definitions:
            for definition in definitions:
                logger.debug('get_attributes: looking for %s' % definition)
                field_name = get_profile_field_name_from_definition(definition)
                if not field_name:
                    '''
                        Profile model may be extended without modifying the
                        mapping file if the attribute name is the same as the
                        definition
                    '''
                    logger.debug('get_attributes: \
                        field name will be the definition')
                    field_name = definition
                if field_name in user_profile._meta.get_all_field_names():
                    fields.append((field_name, definition))
                else:
                    logger.debug('get_attributes: Field not found in profile')
        else:
            fields = [(field_name,
                        get_definition_from_profile_field_name(field_name)) \
                        for field_name \
                            in user_profile._meta.get_all_field_names() \
                        if get_definition_from_profile_field_name(field_name)]
        for field_name, definition in fields:
            field = user_profile._meta.get_field_by_name(field_name)[0]
            logger.debug('get_attributes: found field %s aka %s' \
                % (field_name, field.verbose_name))
            value = getattr(user_profile, field_name)
            if value:
                logger.debug('get_attributes: found value %s' % value)
                attr = {}
                attr['definition'] = definition
                attr['values'] = [value]
                data.append(attr)
            else:
                logger.debug('get_attributes: no value found')
    except (SiteProfileNotAvailable, ObjectDoesNotExist):
        logger.debug('get_attributes: No user profile')
        return None
    attributes[SOURCE_NAME] = data
    return attributes
