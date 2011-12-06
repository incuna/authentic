import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

import authentic2.saml.models as models
import authentic2.idp.saml.saml2_endpoints as saml2_endpoints
import authentic2.saml.common as common

logger = logging.getLogger('authentic2.idp.saml.backend')


class SamlBackend(object):
    def service_list(self, request):
        q = models.LibertyServiceProvider.objects.filter(enabled = True)
        list = []
        for service_provider in q:
            liberty_provider = service_provider.liberty_provider
            policy = common.get_sp_options_policy(liberty_provider)
            if policy and policy.idp_initiated_sso:
                entity_id = liberty_provider.entity_id
                if liberty_provider.protocol_conformance < 3:
                    protocol = 'idff12'
                else:
                    protocol = 'saml2'
                uri = '/idp/%s/idp_sso/' %protocol
                name = '%s login' %liberty_provider.name
                provider_id = entity_id
                list.append((uri, name, provider_id))
                if models.LibertySession.objects.filter(
                        django_session_key=request.session.session_key,
                        provider_id=entity_id).exists():
                    uri = '/idp/%s/idp_slo/' %protocol
                    name = liberty_provider.name + ' logout'
                    provider_id = entity_id
                    list.append((uri, name, provider_id))
        return list

    def logout_list(self, request):
        all_sessions = models.LibertySession.objects.filter(
                django_session_key=request.session.session_key)
        logger.debug("logout_list: all_sessions %s" % str(all_sessions))
        provider_ids = set([s.provider_id for s in all_sessions])
        logger.debug("logout_list: provider_ids %s" % str(provider_ids))
        result = []
        for pid in provider_ids:
            name = pid
            try:
                name = models.LibertyProvider.objects.get(entity_id=pid).name
            except models.LibertyProvider.DoesNotExist:
                pass
            logger.debug("logout_list: name %s" % str(name))
            code = '<div>'
            code += _('Sending logout to %(name)s....') % { 'name': name}
            code += '<iframe src="%s?provider_id=%s" marginwidth="0" marginheight="0" \
scrolling="no" style="border: none" width="16" height="16"></iframe></div>' % \
                    (reverse(saml2_endpoints.idp_slo, args=[pid]), pid)
            logger.debug("logout_list: code %s" % str(code))
            result.append(code)
        return result

    def can_synchronous_logout(self, django_sessions_keys):
        return True
