from django.core.urlresolvers import reverse

import views

class OpenIDMiddleware(object):
    '''Add OpenID discovery header to all responses,
       if Accept header is 'application/xrds+xml' also return an XRDS document.
    '''
    def process_response(self, request, response):
        response['X-XRDS-Location'] = request.build_absolute_uri(
                reverse('openid_xrds'))
        if request.META.get('HTTP_ACCEPT') = 'application/xrds+xml':
            return views.openid_xrds(request)
        return response
