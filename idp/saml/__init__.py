from authentic.idp import register_service_list
import urllib

def saml_service_list(request):
    from authentic.saml.models import LibertyServiceProvider
    q = LibertyServiceProvider.objects.filter(enabled = True, idp_initiated_sso = True)
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

register_service_list(saml_service_list)
