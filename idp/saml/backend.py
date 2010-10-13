import urllib

import authentic.saml.models as models

class SamlBackend(object):
    def service_list(self, request):
        q = models.LibertyServiceProvider.objects.filter(enabled = True, idp_initiated_sso = True)
        list = []
        for service_provider in q:
            liberty_provider = service_provider.liberty_provider
            entity_id = liberty_provider.entity_id
            if liberty_provider.protocol_conformance < 3:
                protocol = 'idff12'
            else:
                protocol = 'saml2'
            uri = '/idp/%s/idp_sso/%s' % (protocol, urllib.quote(entity_id, ''))
            name = liberty_provider.name
            list.append((uri, name))
        return list

    def logout_list(self, request):
        return [ ]
