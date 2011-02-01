from django import template
from django.template.defaultfilters import stringfilter

import urllib2

register = template.Library()

@stringfilter
def urlfullencode(value):
    return urllib2.quote(value, safe='')

register.filter('urlfullencode', urlfullencode)
