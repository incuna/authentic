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
import lasso


from attribute_aggregator.models import AttributeSource
from attribute_aggregator.mapping import ATTRIBUTE_MAPPING
from attribute_aggregator.core import get_def_name_from_oid, \
    get_def_name_from_name_and_ns_of_attribute, \
    load_or_create_user_profile, get_oid_from_def_name, \
    get_attribute_name_in_namespace, get_definition_from_alias, \
    get_attribute_friendly_name_in_namespace

from authentic2.saml.models import LibertyProvider, \
    get_attribute_policy_from_entity_id


logger = logging.getLogger('authentic2.idp.attributes')


def add_data_to_dic(attributes, name, values,
        format=lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI,
        namespace_out='Default', required=False):
    logger.debug('add_data_to_dic: dic is at beginning %s' % attributes)
    logger.debug('add_data_to_dic: ask to add %s with %s and values %s' \
        % (name, format, str(values)))
    if format == lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI:
        if namespace_out == 'Default':
            logger.debug('add_data_to_dic: out in default')
            if (get_oid_from_def_name(name),
                lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, name) in attributes:
                old_values = attributes[(get_oid_from_def_name(name),
                    lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, name)]
                for value in values:
                    if not value in old_values:
                        old_values.append(value)
                attributes[(get_oid_from_def_name(name),
                    lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, name)] = \
                        old_values
                logger.debug('add_data_to_dic: updated %s %s %s %s' \
                    % (get_oid_from_def_name(name),
                    lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, name,
                    str(old_values)))
            else:
                attributes[(get_oid_from_def_name(name),
                    lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, name)] = values
                logger.debug('add_data_to_dic: added %s %s %s %s' \
                    % (get_oid_from_def_name(name),
                    lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, name, str(values)))
        else:
            logger.debug('add_data_to_dic: out in %s' \
                % namespace_out)
            name_in_ns = get_attribute_name_in_namespace(name, namespace_out)
            if name_in_ns:
                fn = \
                get_attribute_friendly_name_in_namespace(name, namespace_out)
                if fn:
                    if (name_in_ns, lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI,
                            fn) in attributes:
                        old_values = attributes[(name_in_ns,
                            lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, fn)]
                        for value in values:
                            if not value in old_values:
                                old_values.append(value)
                        attributes[(name_in_ns,
                            lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, fn)] = \
                                old_values
                        logger.debug('add_data_to_dic: updated %s %s %s %s' \
                            % (name_in_ns,
                            lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, fn,
                            str(old_values)))
                    else:
                        attributes[(name_in_ns,
                            lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, fn)] \
                                = values
                        logger.debug('add_data_to_dic: added %s %s %s %s' \
                            % (name_in_ns,
                            lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI,
                            fn, str(values)))
                else:
                    if (name_in_ns, lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI) \
                            in attributes:
                        old_values = attributes[(name_in_ns,
                            lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI)]
                        for value in values:
                            if not value in old_values:
                                old_values.append(value)
                        attributes[(name_in_ns,
                            lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI)] = \
                                old_values
                        logger.debug('add_data_to_dic: updated %s %s %s' \
                            % (name_in_ns,
                            lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI,
                            str(old_values)))
                    else:
                        attributes[(name_in_ns,
                            lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI)] = values
                        logger.debug('add_data_to_dic: added %s %s %s' \
                            % (name_in_ns,
                            lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI,
                            str(values)))
            elif required:
                raise Exception('Missing a required attribute')
            else:
                logger.info('add_data_to_dic: The attribute %s \
                    is not found in %s' % (name, namespace_out))
    else:
        if namespace_out == 'Default':
            logger.debug('add_data_to_dic: out in default')
            if (name, lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC) \
                    in attributes:
                old_values = attributes[(name,
                    lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC)]
                for value in values:
                    if not value in old_values:
                        old_values.append(value)
                attributes[(name,
                    lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC)] = \
                        old_values
                logger.debug('add_data_to_dic: updated %s %s %s' \
                    % (name,
                    lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC,
                    str(old_values)))
            else:
                attributes[(name,
                    lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC)] = values
                logger.debug('add_data_to_dic: added %s %s %s' % (name,
                    lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC, str(values)))
        else:
            logger.debug('add_data_to_dic: out in %s' \
                % namespace_out)
            name_in_ns = get_attribute_name_in_namespace(name, namespace_out)
            if name_in_ns:
                if (name_in_ns, lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC) \
                        in attributes:
                    old_values = attributes[(name_in_ns,
                        lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC)]
                    for value in values:
                        if not value in old_values:
                            old_values.append(value)
                    attributes[(name_in_ns,
                        lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC)] = \
                            old_values
                    logger.debug('add_data_to_dic: updated %s %s %s' \
                        % (name_in_ns,
                        lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC,
                        str(old_values)))
                else:
                    attributes[(name_in_ns,
                        lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC)] = values
                    logger.debug('add_data_to_dic: added %s %s %s' \
                        % (name_in_ns,
                        lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC, str(values)))
            elif required:
                raise Exception('Missing a required attribute')
            else:
                logger.info('add_data_to_dic: The attribute %s \
                    is not found in %s' % (name, namespace_out))
    logger.debug('add_data_to_dic: dic is now %s' % attributes)


def provide_attributes_at_sso(request, user, audience, **kwargs):
    '''This function is called by a service provider asynrhonous binding at
    sso login. The call is made by the signal add_attributes_to_response.
    In parameter, the service provider id and the user authenticated.'''
    if not user or not audience:
        return None
    logger.debug('provide_attributes_at_sso: search attribute for %s' \
                    % user)
    logger.debug('provide_attributes_at_sso: attributes for %s' \
                    % audience)
    attribute_policy = get_attribute_policy_from_entity_id(audience)
    if not attribute_policy:
        logger.debug('provide_attributes_at_sso: no attribute policy found \
            for %s' % audience)
        return None

    p = load_or_create_user_profile(user=user)
    if not p:
        logger.error('provide_attributes_at_sso: unable to load or create a \
            profile for %s' % user)
        return None
    logger.debug('provide_attributes_at_sso: profile loaded %s' % p)

    '''Returned dictionnary'''
    dic = dict()
    attributes = dict()

    list_pull = attribute_policy.attribute_list_for_sso_from_pull_sources
    if not list_pull:
        logger.debug('provide_attributes_at_sso: no attribute list found \
            from pull source')
    else:
        logger.debug('provide_attributes_at_sso: found attribute list named \
            %s' % list_pull.name)
        l = list_pull.attributes.all()
        if not l:
            logger.debug('provide_attributes_at_sso: The list is empty')
        else:
            logger.debug('provide_attributes_at_sso: the list contains %s' \
                % [a for a in l])
            logger.debug('provide_attributes_at_sso: load in profile %s' \
                % [a.attribute_name for a in l])
            p.load_listed_attributes([a.attribute_name \
                for a in l if not a.source])
            l_with_source = dict()
            for a in l:
                if a.source:
                    if a.source in l_with_source:
                        l_with_source[a.source].append(a.attribute_name)
                    else:
                        l_with_source[a.source] = [a.attribute_name]
            for source, defs in l_with_source.items():
                p.load_listed_attributes_with_source(defs, source)

            for a in l:
                data = None
                if a.source:
                    logger.debug('provide_attributes_at_sso: %s must be \
                        provided by %s' % (a.attribute_name, a.source))
                    data = \
                        p.get_data_of_definition_and_source(\
                            a.attribute_name, a.source)
                else:
                    data = p.get_data_of_definition(a.attribute_name)
                '''The freshest'''
                if not data:
                    logger.debug('provide_attributes_at_sso: %s not found' \
                        % a.attribute_name)
                    if attribute_policy.\
                        send_error_and_no_attrs_if_missing_required_attrs \
                        and a.required:
                        raise Exception('Missing a required attribute')
                else:
                    logger.debug('provide_attributes_at_sso: found %s' \
                        % [x.__unicode__() for x in data])
#           d = data.sort(key=lambda x: x.expiration_date, reverse=True)[0]
                    d = data[0]
                    try:
                        add_data_to_dic(attributes, a.attribute_name,
                            d.get_values(),
                            a.output_name_format,
                            a.output_namespace,
                            # Send error if required and attribute required
                            (attribute_policy.\
                        send_error_and_no_attrs_if_missing_required_attrs \
                            and a.required))
                    except:
                        # Missing required attribute
                        pass

            logger.debug('provide_attributes_at_sso: attributes returned \
                from pull source %s' % str(attributes))

    if attribute_policy.forward_attributes_from_push_sources \
            and request and request.session \
            and 'multisource_attributes' in request.session:
        '''
            Treat attributes in session
        '''
        logger.debug('provide_attributes_at_sso: attributes is session are \
            %s' % str(request.session['multisource_attributes']))
        attrs = {}
        sources = \
                attribute_policy.source_filter_for_sso_from_push_sources.all()
        if sources:
            s_names = [s.name for s in sources]
            logger.debug('provide_attributes_at_sso: filter attributes from \
                push source, sources accepted are %s' % str(s_names))
            for entity_id, l \
                    in request.session['multisource_attributes'].items():
                if entity_id in s_names:
                    for token in l:
                        if 'attributes' in token:
                            logger.debug('provide_attributes_at_sso: \
                                keep in dic %s' \
                                % str({entity_id: token['attributes']}))
                            attrs.update({entity_id: token['attributes']})
        else:
            for entity_id, l \
                    in request.session['multisource_attributes'].items():
                for token in l:
                    if 'attributes' in token:
                        logger.debug('provide_attributes_at_sso: \
                            keep in dic %s' \
                            % str({entity_id: token['attributes']}))
                        attrs.update({entity_id: token['attributes']})

        logger.debug('provide_attributes_at_sso: attributes are %s' \
            % str(attrs))

        if not attribute_policy.map_attributes_from_push_sources \
                and not \
                attribute_policy.attribute_filter_for_sso_from_push_sources:
            #TODO: Load in profile if possible
            for vals in attrs.values():
                attributes.update(vals)

        else:
            dic_to_load_in_profile = dict()
            definitions = list()
            for entity_id, attrs_list in attrs.items():
                source = None
                if attribute_policy.map_attributes_from_push_sources:
                    try:
                        source = AttributeSource.objects.get(name=entity_id)
                    except:
                        try:
                            lp = \
                            LibertyProvider.objects.get(entity_id=entity_id)
                            source = AttributeSource.objects.get(name=lp.name)
                        except:
                            pass
                namespace_in = 'Default'
                if not source:
                    logger.debug('provide_attributes_at_sso: Not \
                        attribute source found for %s' \
                        % str(attributes))
                else:
                    logger.debug('provide_attributes_at_sso: Source \
                        found %s' % source.name)
                    namespace_in = source.namespace
                logger.debug('provide_attributes_at_sso: \
                    input namespace is %s' % namespace_in)
                dic_to_load_in_profile[entity_id] = list()
                for key, values in attrs_list.items():
                    logger.debug('provide_attributes_at_sso: treat \
                        %s' % str(attrs))
                    found = False
                    try:
                        name, format, fname = key
                        found = True
                    except:
                        try:
                            name, format = key
                            found = True
                        except:
                            try:
                                name = key
                                found = True
                            except:
                                pass
                    if found:
                        logger.debug('provide_attributes_at_sso: \
                            attribute with name %s' % str(name))
                        if namespace_in == 'Default':
                            definition = None
                            if name in ATTRIBUTE_MAPPING:
                                definition = name
                            else:
                                definition = get_def_name_from_oid(name)
                                if not definition:
                                    definition = \
                                        get_definition_from_alias(name)
                            if definition:
                                logger.debug('provide_attributes_at_sso: \
                                    found definition %s' % definition)
                                definitions.append(definition)
                                dic_to_load_in_profile[entity_id].\
                                    append({'definition': definition,
                                        'values': values})
                        else:
                            definition = \
                            get_def_name_from_name_and_ns_of_attribute(name,
                                namespace_in)
                            if definition:
                                logger.debug('provide_attributes_at_sso: \
                                    found definition %s' % definition)
                                definitions.append(definition)
                                dic_to_load_in_profile[entity_id].\
                                    append({'name': name,
                                        'namespace': namespace_in,
                                        'values': values})
                    else:
                        logger.debug('provide_attributes_at_sso: \
                            unknown format')

            '''
                Load in profile to deal with input mapping
            '''
            logger.debug('provide_attributes_at_sso: \
                load in profile %s' % str(dic_to_load_in_profile))
            p.load_by_dic(dic_to_load_in_profile)

            if attribute_policy.attribute_filter_for_sso_from_push_sources:
                att_l = attribute_policy.\
                    attribute_filter_for_sso_from_push_sources.\
                        attributes.all()
                if att_l:
                    for att in att_l:
                        d = None
                        if attribute_policy.\
                                filter_source_of_filtered_attributes \
                                and att.source:
                            d = p.get_data_of_definition_and_source(\
                                att.attribute_name, att.source)
                            if d:
                                d = d[0]
                        else:
                            d = p.get_freshest_data_of_definition(\
                                att.attribute_name)
                        if d:
                            namespace_out = 'Default'
                            name_format_out = \
                                lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI
                            if attribute_policy.\
                                    map_attributes_of_filtered_attributes:
                                namespace_out = att.output_namespace
                                name_format_out = att.output_name_format
                            elif attribute_policy.\
                                    map_attributes_from_push_sources:
                                namespace_out = \
                                    attribute_policy.output_namespace
                                name_format_out = \
                                    attribute_policy.attribute_name_format
                            logger.debug('provide_attributes_at_sso: \
                                output namespace %s' % namespace_out)
                            logger.debug('provide_attributes_at_sso: \
                                output format %s' % name_format_out)
                            add_data_to_dic(attributes,
                                d.definition,
                                d.get_values(),
                                name_format_out,
                                namespace_out,
                                (attribute_policy.\
                        send_error_and_no_attrs_if_missing_required_attrs \
                                and att.required))
            else:
                namespace_out = 'Default'
                name_format_out = lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI
                if attribute_policy.map_attributes_from_push_sources:
                    namespace_out = attribute_policy.output_namespace
                    name_format_out = attribute_policy.output_name_format
                for definition in definitions:
                    d = p.get_freshest_data_of_definition(definition)
                    add_data_to_dic(attributes,
                        d.definition,
                        d.get_values(),
                        name_format_out,
                        namespace_out)

    logger.debug('provide_attributes_at_sso: attributes returned are \
        %s' % str(attributes))

    dic['attributes'] = attributes
    return dic
