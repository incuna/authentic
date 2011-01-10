# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 fdm=indent : */
# some code from http://www.djangosnippets.org/snippets/310/ by simon
# and from examples/djopenid from python-openid-2.2.4

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

from django.contrib.auth import REDIRECT_FIELD_NAME

from openid.consumer.discover import OPENID_IDP_2_0_TYPE, OPENID_2_0_TYPE
from openid.fetchers import HTTPFetchingError
from openid.server.server import Server
from openid.server.trustroot import verifyReturnTo
from openid.yadis.discover import DiscoveryFailure
from openid.yadis.constants import YADIS_CONTENT_TYPE

from utils import add_sreg_data, get_store

@csrf_exempt
def openid_server(request):
    """
    This view is the actual OpenID server - running at the URL pointed to by 
    the <link rel="openid.server"> tag. 
    """
    server = Server(get_store(request),
        op_endpoint=request.build_absolute_uri(reverse('openid-provider-root')))

    # Clear AuthorizationInfo session var, if it is set
    if request.session.get('AuthorizationInfo', None):
        del request.session['AuthorizationInfo']

    querydict = dict(request.REQUEST.items())
    orequest = server.decodeRequest(querydict)
    if not orequest:
        orequest = request.session.get('OPENID_REQUEST', None)
        if orequest:
            # remove session stored data:
            del request.session['OPENID_REQUEST']
        else:
            # not request, render info page:
            return render_to_response('openid_provider/server.html', {
                'host': request.build_absolute_uri('/'),
                'xrds_location': request.build_absolute_uri(
                    reverse('openid-provider-xrds')),
            }, context_instance=RequestContext(request))

    if orequest.mode in ("checkid_immediate", "checkid_setup"):
        if not request.user.is_authenticated():
            return landing_page(request, orequest)

        openid = openid_is_authorized(request, orequest.identity, orequest.trust_root)

        if openid is not None:
            id_url = request.build_absolute_uri(
                reverse('openid-provider-identity', args=[openid.openid]))
            oresponse = orequest.answer(True, identity=id_url)
        elif orequest.immediate:
            raise Exception('checkid_immediate mode not supported')
        else:
            request.session['OPENID_REQUEST'] = orequest
            return HttpResponseRedirect(reverse('openid-provider-decide'))
    else:
        oresponse = server.handleRequest(orequest)
    if request.user.is_authenticated():
        add_sreg_data(request, orequest, oresponse)
    # Convert a webresponse from the OpenID library in to a Django HttpResponse
    webresponse = server.encodeResponse(oresponse)
    response = HttpResponse(webresponse.body)
    response.status_code = webresponse.code
    for key, value in webresponse.headers.items():
        response[key] = value
    return response

def openid_xrds(request, identity=False, id=None):
    if identity:
        types = [OPENID_2_0_TYPE]
    else:
        types = [OPENID_IDP_2_0_TYPE]
    endpoints = [request.build_absolute_uri(reverse('openid-provider-root'))]
    return render_to_response('openid_provider/xrds.xml', {
        'host': request.build_absolute_uri('/'),
        'types': types,
        'endpoints': endpoints,
    }, context_instance=RequestContext(request), mimetype=YADIS_CONTENT_TYPE)

def openid_decide(request):
    """
    The page that asks the user if they really want to sign in to the site, and
    lets them add the consumer to their trusted whitelist.
    # If user is logged in, ask if they want to trust this trust_root
    # If they are NOT logged in, show the landing page
    """
    orequest = request.session.get('OPENID_REQUEST')

    if not request.user.is_authenticated():
        return landing_page(request, orequest)

    openid = openid_get_identity(request, orequest.identity)
    if openid is None:
        return error_page(request, "You are signed in but you don't have OpenID here!")

    if request.method == 'POST' and request.POST.get('decide_page', False):
        openid.trustedroot_set.create(trust_root=orequest.trust_root)
        return HttpResponseRedirect(reverse('openid-provider-root'))

    # verify return_to of trust_root
    try:
        trust_root_valid = verifyReturnTo(orequest.trust_root, orequest.return_to) and "Valid" or "Invalid"
    except HTTPFetchingError:
        trust_root_valid = "Unreachable"
    except DiscoveryFailure:
        trust_root_valid = "DISCOVERY_FAILED"

    return render_to_response('openid_provider/decide.html', {
        'title': _('Trust this site?'),
        'trust_root': orequest.trust_root,
        'trust_root_valid': trust_root_valid,
        'identity': orequest.identity,
    }, context_instance=RequestContext(request))

def error_page(request, msg):
    return render_to_response('error.html', {
        'title': _('Error'),
        'msg': msg,
    }, context_instance=RequestContext(request))

def landing_page(request, orequest):
    """
    The page shown when the user attempts to sign in somewhere using OpenID 
    but is not authenticated with the site. For idproxy.net, a message telling
    them to log in manually is displayed.
    """
    request.session['OPENID_REQUEST'] = orequest
    login_url = settings.LOGIN_URL
    path = request.get_full_path()
    url = '%s?%s=%s' % (login_url, REDIRECT_FIELD_NAME, urlquote(path))
    return HttpResponseRedirect(url)

def openid_is_authorized(request, identity_url, trust_root):
    """
    Check that they own the given identity URL, and that the trust_root is 
    in their whitelist of trusted sites.
    """
    if not request.user.is_authenticated():
        return None

    openid = openid_get_identity(request, identity_url)
    if openid is None:
        return None

    if openid.trustedroot_set.filter(trust_root=trust_root).count() < 1:
        return None

    return openid

def openid_get_identity(request, identity_url):
    """
    Select openid based on claim (identity_url).
    If none was claimed identity_url will be 'http://specs.openid.net/auth/2.0/identifier_select'
    - in that case return default one
    - if user has no default one, return any
    - in other case return None!
    """
    for openid in request.user.openid_set.iterator():
        if identity_url == request.build_absolute_uri(
                reverse('openid-provider-identity', args=[openid.openid])):
            return openid
    if identity_url == 'http://specs.openid.net/auth/2.0/identifier_select':
        # no claim was made, choose user default openid:
        openids = request.user.openid_set.filter(default=True)
        if openids.count() == 1:
            return openids[0]
        return request.user.openid_set.all()[0]
    return None
