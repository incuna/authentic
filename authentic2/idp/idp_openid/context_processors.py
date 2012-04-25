from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

def get_url():
    return reverse('openid-provider-xrds')

def openid_meta(request):
    context = {
        'openid_server': request.build_absolute_uri(get_url())
    }
    content = mark_safe('''<meta http-equiv="X-XRDS-Location" content="%(openid_server)s"/>
    <meta http-equiv="X-YADIS-Location" content="%(openid_server)s" />
''' % context)
    return { 'openid_meta': content }
