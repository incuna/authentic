# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 fdm=indent : */
# some code from http://www.djangosnippets.org/snippets/310/ by simon
# and from examples/djopenid from python-openid-2.2.4

import logging
import hashlib
import urlparse

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    from django.contrib.csrf.middleware import csrf_exempt
import django.forms as forms


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

from utils import get_store, oresponse_to_response
from authentic2.auth2_auth.views import redirect_to_login
import models

logger = logging.getLogger('authentic.idp.idp_openid')


def check_exploded(exploded, request):
    username = request.user.username
    return not exploded.path.startswith(request.path) \
       or exploded.path[len(request.path):].strip('/') != username \
       or exploded.params \
       or exploded.query  \
       or exploded.fragment

@csrf_exempt
def openid_server(request):
    """
    This view is the actual OpenID server - running at the URL pointed to by 
    the <link rel="openid.server"> tag. 
    """
    server = Server(get_store(request),
        op_endpoint=request.build_absolute_uri(
            reverse('openid-provider-root')))

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
    logger.debug('SREG request: %s' % sreg_request.__dict__)

    if orequest.mode in ("checkid_immediate", "checkid_setup"):
        # User is not logged
        if not request.user.is_authenticated():
            # Site does not want interaction
            if orequest.immediate:
                logger.debug('User not logged and checkid immediate request, \
returning OpenID failure')
                return oresponse_to_response(server, orequest.answer(False))
            else:
            # Try to login
                request.session['OPENID_REQUEST'] = orequest
                logger.debug('User not logged and checkid request, \
redirecting to login page')
                return redirect_to_login(request, nonce='1')
        else:
            identity = orequest.identity
            if identity != IDENTIFIER_SELECT:
               exploded = urlparse.urlparse(identity)
               # Allows only /openid/<user_id>
               if check_exploded(exploded, request):
                   # We only support directed identity
                   logger.debug('Invalid OpenID identity %s' % identity)
                   return oresponse_to_response(server, orequest.answer(False))
            try:
                trusted_root = models.TrustedRoot.objects.get(
                        user=request.user.id, trust_root=orequest.trust_root)
                # Check the choices are sufficient
                if not set(sreg_request.required)\
                        .issubset(set(trusted_root.choices)):
                    # Current assertion is not sufficent, ask again !
                    if orequest.immediate:
                        logger.debug('Attributes authorization unsufficient \
and checkid immediate, returning OpenID failure')
                        return oresponse_to_response(server,
                                orequest.answer(False))
                    request.session['OPENID_REQUEST'] = orequest
                    logger.debug('Attributes authorization unsufficient \
for %s, redirecting to consent page' % orequest.trust_root)
                    return HttpResponseRedirect(
                            reverse('openid-provider-decide'))
                user_data = {}
                for field in trusted_root.choices:
                    if field == 'email':
                        user_data[field] = request.user.email
                    elif field == 'fullname':
                        user_data[field] = '%s %s' % (request.user.first_name,
                                request.user.last_name)
                    elif field == 'nickname':
                        user_data[field] = getattr(request.user, 'username',
                                '')
                    else:
                        logger.debug('Could not provide SReg field %s' % field)
            except models.TrustedRoot.MultipleObjectsReturned:
                # Too much trustedroots remove
                models.TrustedRoot.objects.filter(user=request.user.id,
                        trust_root=orequest.trust_root).delete()
                # RP does not want any interaction
                if orequest.immediate:
                    logger.warning('Too much trusted root records and \
checkid immediate, returning OpenID failure')
                    return oresponse_to_response(server,
                            orequest.answer(False))
                request.session['OPENID_REQUEST'] = orequest
                logger.info('Too much trusted root for %s, redirecting to \
consent page' % orequest.trust_root)
                return HttpResponseRedirect(reverse('openid-provider-decide'))
            except models.TrustedRoot.DoesNotExist:
                # RP does not want any interaction
                if orequest.immediate:
                    logger.info('Trusted root unknown and checkid \
immediate, returning OpenID failure')
                    return oresponse_to_response(server,
                            orequest.answer(False))
                request.session['OPENID_REQUEST'] = orequest
                logger.info('Trusted root %s unknown, redirecting to \
consent page' % orequest.trust_root)
                return HttpResponseRedirect(reverse('openid-provider-decide'))

        # Create a directed identity if needed
        if identity == IDENTIFIER_SELECT:
            hash = hashlib.sha1(str(request.user.id)+'|'+orequest.trust_root) \
                    .hexdigest()
            claimed_id = request.build_absolute_uri(
                    reverse('openid-provider-identity', args=[hash]))
            logger.info('Giving directed identity %r to trusted root %r \
with sreg data %s' % (claimed_id, orequest.trust_root, user_data))
        else:
            claimed_id = identity
            logger.info('Giving claimed identity %r to trusted root %r \
with sreg data %s' % (claimed_id, orequest.trust_root, user_data))

        oresponse = orequest.answer(True, identity=claimed_id)
        sreg_response = SRegResponse.extractResponse(sreg_request, user_data)
        oresponse.addExtension(sreg_response)
    else:
        oresponse = server.handleRequest(orequest)
    logger.info('Returning OpenID response %s' % oresponse)
    return oresponse_to_response(server, oresponse)

def openid_xrds(request, identity=False, id=None):
    '''XRDS discovery page'''
    logger.debug('OpenID XRDS identity:%(identity)s id:%(id)s' % locals())
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
    def __init__(self, sreg_request=None, *args, **kwargs):
        super(DecideForm, self).__init__(*args, **kwargs)
        for field in sreg_request.optional:
            self.fields[str(field)] = forms.BooleanField(
                    label=data_fields[str(field)], required=False)
        logger.info('3SREG request: %s' % self.fields)

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
        logger.warning('OpenID decide view failed, \
because no OpenID request is saved')
        return HttpResponseRedirect('/')
    sreg_request = SRegRequest.fromOpenIDRequest(orequest)
    logger.debug('SREG request: %s' % sreg_request.__dict__)
    if not request.user.is_authenticated():
        # Not authenticated ? Authenticate and go back to the server endpoint
        return redirect_to_login(request, next=reverse(openid_server),
                nonce='1')

    if request.method == 'POST':
        if 'cancel' in request.POST:
            # User refused
            logger.info('OpenID decide canceled')
            return HttpResponseRedirect('%s?cancel' % reverse(openid_server))
        else:
            form = DecideForm(sreg_request=sreg_request, data=request.POST)
            if form.is_valid():
                data = form.cleaned_data
                # Remember the choice
                t, created = models.TrustedRoot.objects.get_or_create(
                        user=request.user.id, trust_root=orequest.trust_root)
		t.choices = sreg_request.required \
                    + [ field for field in data if data[field] ]
                t.save()
                logger.debug('OpenID decide, user choice:%s' % data)
                return HttpResponseRedirect(reverse('openid-provider-root'))
    else:
        form = DecideForm(sreg_request=sreg_request)
    logger.info('OpenID device view, orequest:%s' % orequest)

    # verify return_to of trust_root
    try:
        trust_root_valid = verifyReturnTo(orequest.trust_root,
                orequest.return_to) and "Valid" or "Invalid"
    except HTTPFetchingError:
        trust_root_valid = "Unreachable"
    except DiscoveryFailure:
        trust_root_valid = "DISCOVERY_FAILED"

    return render_to_response('idp/openid/decide.html', {
        'title': _('Trust this site?'),
        'required': sreg_request.required,
        'optional': sreg_request.optional,
        'trust_root_valid': trust_root_valid,
        'form': form,
    }, context_instance=RequestContext(request))

def openid_discovery(request, id):
    '''HTML discovery page'''
    xrds_url = request.build_absolute_uri(
            reverse('openid-provider-identity-xrds', args=[id]))
    response = render_to_response('idp/openid/discovery.html', {
        'xrds': xrds_url,
        'openid_server': request.build_absolute_uri(
            reverse('openid-provider-root'))
    }, context_instance=RequestContext(request))
    response['X-XRDS-Location'] = xrds_url
    return response
