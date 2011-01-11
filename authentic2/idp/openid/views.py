# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 fdm=indent : */
# some code from http://www.djangosnippets.org/snippets/310/ by simon
# and from examples/djopenid from python-openid-2.2.4

import logging
import hashlib
import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.utils.http import urlquote
try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    from django.contrib.csrf.middleware import csrf_exempt
import django.forms as forms

from django.contrib.auth import REDIRECT_FIELD_NAME

from openid.consumer.discover import OPENID_IDP_2_0_TYPE, \
    OPENID_2_0_TYPE, OPENID_1_0_TYPE, OPENID_1_1_TYPE
from openid.fetchers import HTTPFetchingError
from openid.server.server import Server, ProtocolError
from openid.server.trustroot import verifyReturnTo
from openid.yadis.discover import DiscoveryFailure
from openid.yadis.constants import YADIS_CONTENT_TYPE
from openid.message import IDENTIFIER_SELECT
from openid.extensions.sreg import ns_uri as SREG_TYPE, SRegRequest, \
        SRegResponse, data_fields

from utils import add_sreg_data, get_store, oresponse_to_response
from authentic2.auth.views import redirect_to_login
import models

logger = logging.getLogger('authentic.idp.openid')

@csrf_exempt
def openid_server(request):
    """
    This view is the actual OpenID server - running at the URL pointed to by 
    the <link rel="openid.server"> tag. 
    """
    server = Server(get_store(request),
        op_endpoint=request.build_absolute_uri(reverse('openid-provider-root')))

    # Cancellation
    if 'cancel' in request.REQUEST:
        if 'OPENID_REQUEST' in request.session:
            return oresponse_to_response(server,
                request.session['OPENID_REQUEST'].answer(False))
        else:
            return HttpResponseRedirect('/')

    # Clear AuthorizationInfo session var, if it is set
    if request.session.get('AuthorizationInfo', None):
        del request.session['AuthorizationInfo']

    querydict = dict(request.REQUEST.items())
    try:
        orequest = server.decodeRequest(querydict)
    except ProtocolError, why:
        logger.error('Invalid OpenID message %s' % querydict)
        return oresponse_to_response(server, why)
    if not orequest:
        orequest = request.session.get('OPENID_REQUEST', None)
        if orequest:
            logger.info('Restarting saved request by %s' % orequest.trust_root)
            # remove session stored data:
            pass
            # del request.session['OPENID_REQUEST']
        else:
            logger.info('No OpenID request redirecting to homepage')
            return HttpResponseRedirect('/')
    else:
        logger.info('Received OpenID request: %s' % querydict)
    sreg_request = SRegRequest.fromOpenIDRequest(orequest)

    if orequest.mode in ("checkid_immediate", "checkid_setup"):
        # User is not logged
        if not request.user.is_authenticated():
            # Site does not want interaction
            if orequest.immediate:
                logger.info('User not logged and checkid immediate request, returning OpenID failure')
                return oresponse_to_response(server, orequest.answer(False))
            else:
            # Try to login
                request.session['OPENID_REQUEST'] = orequest
                logger.info('User not logged and checkid request, redirecting to login page')
                return redirect_to_login(request, nonce='1')
        else:
            identity = orequest.identity
            if identity != IDENTIFIER_SELECT:
               exploded = urlparse.urlparse(identity)
               logger.debug('exploded %r' % ((exploded, request.path, exploded.path[len(request.path):].strip('/')),))
               # Allows only /openid/<user_id>
               if not exploded.path.startswith(request.path) \
                   or not exploded.path[len(request.path):].strip('/') == request.user.username \
                   or exploded.params \
                   or exploded.query  \
                   or exploded.fragment :
                   # We only support directed identity
                   logger.info('Invalid OpenID identity %s' % identity)
                   return oresponse_to_response(server, orequest.answer(False))
            try:
                trusted_root = models.TrustedRoot.objects.get(user=request.user.id,
                        trust_root=orequest.trust_root)
                # Check the choices are sufficient
                if not set(sreg_request.required).issubset(set(trusted_root.choices)):
                    # Current assertion is not sufficent, ask again !
                    if orequest.immediate:
                        logger.info('Attributes authorization unsufficient and checkid immediate, returning OpenID failure')
                        return oresponse_to_response(server, orequest.answer(False))
                    request.session['OPENID_REQUEST'] = orequest
                    logger.info('Attributes authorization unssificient for %s, redirecting to consent page' % orequest.trust_root)
                    return HttpResponseRedirect(reverse('openid-provider-decide'))
                user_data = {}
                for field in trusted_root.choices:
                    if field == 'email':
                        user_data[field] = request.user.email
                    elif field == 'fullname':
                        user_data[field] = '%s %s' % (request.user.first_name,
                                request.user.last_name)
                    else:
                        logger.warning('Could not provide SReg field %s' % field)
            except models.TrustedRoot.MultipleObjectsReturned:
                # Too much trustedroots remove
                models.TrustedRoot.objects.filter(user=request.user.id,
			trust_root=orequest.trust_root).delete()
                # RP does not want any interaction
                if orequest.immediate:
                    logger.info('Too much trusted root records and checkid immediate, returning OpenID failure')
                    return oresponse_to_response(server, orequest.answer(False))
                request.session['OPENID_REQUEST'] = orequest
                logger.info('Too much trusted root for %s, redirecting to consent page' % orequest.trust_root)
                return HttpResponseRedirect(reverse('openid-provider-decide'))
            except models.TrustedRoot.DoesNotExist:
                # RP does not want any interaction
                if orequest.immediate:
                    logger.info('Trusted root unknown and checkid immediate, returning OpenID failure')
                    return oresponse_to_response(server, orequest.answer(False))
                request.session['OPENID_REQUEST'] = orequest
                logger.info('Trusted root %s unknown, redirecting to consent page' % orequest.trust_root)
                return HttpResponseRedirect(reverse('openid-provider-decide'))

        # Create a directed identity if needed
        if identity == IDENTIFIER_SELECT:
            hash = hashlib.sha1(str(request.user.id)+'|'+orequest.trust_root).hexdigest()
            claimed_id = request.build_absolute_uri(
                    reverse('openid-provider-identity', args=[hash]))
            logger.info('Giving directed identity %r to trusted root %r with sreg data %s' %
                     (claimed_id, orequest.trust_root, user_data))
        else:
            claimed_id = identity
            logger.info('Giving claimed identity %r to trusted root %r with sreg data %s' %
                     (claimed_id, orequest.trust_root, user_data))

        oresponse = orequest.answer(True, identity=claimed_id)
        sreg_response = SRegResponse.extractResponse(sreg_request, user_data)
        oresponse.addExtension(sreg_response)
    else:
        oresponse = server.handleRequest(orequest)
    return oresponse_to_response(server, oresponse)

def openid_xrds(request, identity=False, id=None):
    if identity:
        types = [OPENID_2_0_TYPE, OPENID_1_0_TYPE, OPENID_1_1_TYPE, SREG_TYPE]
        local_ids = []
    else:
        types = [OPENID_IDP_2_0_TYPE,SREG_TYPE]
        local_ids = []
    endpoints = [request.build_absolute_uri(reverse('openid-provider-root'))]
    return render_to_response('idp/openid/xrds.xml', {
        'host': request.build_absolute_uri('/'),
        'types': types,
        'endpoints': endpoints,
        'local_ids': local_ids,
    }, context_instance=RequestContext(request), mimetype=YADIS_CONTENT_TYPE)

class DecideForm(forms.Form):
    def __init__(self, sreg_request=[], *args, **kwargs):
        super(DecideForm, self).__init__(*args, **kwargs)
        for field in sreg_request.optional:
            self.fields[field] = forms.BooleanField(label=data_fields[field],
                required=False)

def openid_decide(request):
    """
    The page that asks the user if they really want to sign in to the site, and
    lets them add the consumer to their trusted whitelist.
    # If user is logged in, ask if they want to trust this trust_root
    # If they are NOT logged in, show the landing page
    """
    orequest = request.session.get('OPENID_REQUEST')
    # No request ? Failure..
    if not orequest:
        return HttpResponseRedirect('/')
    sreg_request = SRegRequest.fromOpenIDRequest(orequest)
    if not request.user.is_authenticated():
        # Not authenticated ? Authenticate and go back to the server endpoint
        return redirect_to_login(request, next=reverse(openid_server), nonce='1')

    if request.method == 'POST':
        if 'cancel' in request.POST:
            # User refused
            return HttpResponseRedirect('%s?cancel' % reverse(openid_server))
        else:
            form = DecideForm(sreg_request=sreg_request,data=request.POST)
            if form.is_valid():
                data = form.cleaned_data
                # Remember the choice
                t, created = models.TrustedRoot.objects.get_or_create(user=request.user.id,
                        trust_root=orequest.trust_root)
		t.choices = sreg_request.required \
                    + [ field for field in data if data[field] ]
                t.save()
                return HttpResponseRedirect(reverse('openid-provider-root'))
    else:
        form = DecideForm(sreg_request=sreg_request)

    # verify return_to of trust_root
    try:
        trust_root_valid = verifyReturnTo(orequest.trust_root, orequest.return_to) and "Valid" or "Invalid"
    except HTTPFetchingError:
        trust_root_valid = "Unreachable"
    except DiscoveryFailure:
        trust_root_valid = "DISCOVERY_FAILED"

    return render_to_response('idp/openid/decide.html', {
        'title': _('Trust this site?'),
        'required': sreg_request.required,
        'trust_root_valid': trust_root_valid,
        'form': form,
    }, context_instance=RequestContext(request))

def openid_discovery(request, id):
    xrds_url = request.build_absolute_uri(
            reverse('openid-provider-identity-xrds', args=[id]))
    response = render_to_response('idp/openid/discovery.html', {
        'xrds': xrds_url,
        'openid_server': request.build_absolute_uri(
            reverse('openid-provider-root'))
    }, context_instance=RequestContext(request))
    response['X-XRDS-Location'] = xrds_url
    return response
    
