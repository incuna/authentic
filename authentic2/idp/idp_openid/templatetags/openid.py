from django.core.urlresolvers import reverse
from django import template
from django.template import loader, Node, Variable

'''Use in your base.html file like this:

    {% load openid %}
    <html>
    <head>
    {% openid_meta %}
    </head>
'''

register = template.Library()
class OpenIDLinks(Node):
    def render(self, context):
        context = {
                'openid_server': context['request'].build_absolute_uri(
                    reverse('openid-provider-xrds'))
                }
        return '''<meta http-equiv="X-XRDS-Location" content="%(openid_server)s"/>
    <meta http-equiv="X-YADIS-Location" content="%(openid_server)s" />
''' % context


@register.tag
def openid_meta(parser, token):
    '''Display OpenID metadata links.
       
       The template context must contain the request object.'''
    return OpenIDLinks()
