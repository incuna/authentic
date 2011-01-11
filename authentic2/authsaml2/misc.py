from authentic2.authsaml2.models import *

import sys

def attributesMatch(attributes, attributes_to_check):
    attrs = AttributeMapping.objects.filter(map=attributes_to_check)
    for attr in attrs:
        if not attributes[attr.attribute_name]:
            raise Exception('Attribute %s not provided' %attr.attribute_name)
            return False
        if not attr.attribute_value in attributes[attr.attribute_name]:
            raise Exception('Attribute %s has not value %s' %(attr.attribute_name,attr.attribute_value))
            return False
    return True

def isAuthorized(provider, attributes):
    p = IdPOptionsPolicy.objects.filter(name='All', enabled=True)
    if p:
        p = p[0]
        if p.attribute_map:
            return attributesMatch(attributes, p.attribute_map)
        else:
           return True

    if provider.identity_provider.enable_following_policy:
        if provider.identity_provider.attribute_map:
            return attributesMatch(attributes, provider.identity_provider.attribute_map)
        else:
           return True

    p = IdPOptionsPolicy.objects.filter(name='Default', enabled=True)
    if p:
        p = p[0]
        if p.attribute_map:
            return attributesMatch(attributes, p.attribute_map)
        else:
           return True

    raise Exception('No policy defined')
    return False

