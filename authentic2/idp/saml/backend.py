import urllib

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

import authentic2.saml.models as models
import authentic2.idp.saml.saml2_endpoints as saml2_endpoints

class SamlBackend(object):
    def service_list(self, request):
        q = models.LibertyServiceProvider.objects.filter(enabled = True, idp_initiated_sso = True)
        list = []
        for service_provider in q:
            # XXX: Differentiate the services the user knows and the others
            liberty_provider = service_provider.liberty_provider
            entity_id = liberty_provider.entity_id
            if liberty_provider.protocol_conformance < 3:
                protocol = 'idff12'
            else:
                protocol = 'saml2'
            #uri = '/idp/%s/idp_sso/%s' % (protocol, entity_id)
            uri = '/idp/%s/idp_sso/' %protocol
            name = '%s login' %liberty_provider.name
            provider_id = entity_id
            list.append((uri, name, provider_id))
            # XXX: Check services with open sessions
            if models.LibertySession.objects.filter(
                    django_session_key=request.session.session_key,
                    provider_id=entity_id).exists():
                uri = '/idp/%s/idp_slo/%s?next=/' % (protocol, entity_id)
                name = liberty_provider.name + ' logout'
                list.append((uri, name))
        return list

    def logout_list(self, request):
        all_sessions = models.LibertySession.objects.filter(
                django_session_key=request.session.session_key)
        provider_ids = set([s.provider_id for s in all_sessions])
        result = []
        for pid in provider_ids:
            name = pid
            try:
                name = models.LibertyProvider.objects.get(entity_id=pid).name
            except models.LibertyProvider.DoesNotExist:
                pass
            code = '<div>'
            code += _('Sending logout to %(pid)s....') % { 'pid': pid }
            code += '<iframe src="%s" marginwidth="0" marginheight="0" \
scrolling="no" style="border: none" width="16" height="16"></iframe></div>' % \
                    reverse(saml2_endpoints.idp_slo, args=[pid])
            result.append(code)
        return result

    def can_synchronous_logout(self, django_sessions_keys):
        return True
