from django.views.decorators.csrf import csrf_exempt
from openid_provider.views import openid_get_identity
from openid_provider.views import error_page
from openid_provider.views import landing_page
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from openid.server.trustroot import verifyReturnTo
from django.template.loader import get_template
from django.template import Context
from django.views.generic.simple import redirect_to
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from openid.server.server import Server
from django.core.urlresolvers import reverse
import re
from django.template import RequestContext
from django.conf import settings
from openid.server.server import ProtocolError, CheckIDRequest, Message
from django.core.cache import cache

def get_base_uri(req):
        name = req.META['HTTP_HOST']
        try: name = name[:name.index(':')]
        except: pass

        try: port = int(req.META['SERVER_PORT'])
        except: port = 80

        if req.META.get('HTTPS') == 'on':
                proto = 'https'
        else:
                proto = 'http'

        if port in [80, 443] or not port:
                port = ''
        else:
                port = ':%s' % port

        return '%s://%s%s' % (proto, name, port)

def django_response(webresponse):
        "Convert a webresponse from the OpenID library in to a Django HttpResponse"
        response = HttpResponse(webresponse.body)
        response.status_code = webresponse.code
        for key, value in webresponse.headers.items():
                response[key] = value
        return response

@csrf_exempt
def openid_server(req):
    """
    This view is the actual OpenID server - running at the URL pointed to by 
    the <link rel="openid.server"> tag. 
    """
    host = get_base_uri(req)
    try:
        # if we have django_openid_auth in applications directory
        # then we can use DjangoOpenIDStore
        from django_openid_auth.store import DjangoOpenIDStore
        store = DjangoOpenIDStore()
    except:
        # otherwise use FileOpenIDStore
        OPENID_FILESTORE = '/tmp/openid-filestore'
        from openid.store.filestore import FileOpenIDStore
        store = FileOpenIDStore(OPENID_FILESTORE)
        
    server = Server(store, op_endpoint="%s%s" % (host, reverse('openid-provider-root')))

    # Clear AuthorizationInfo session var, if it is set
    if req.session.get('AuthorizationInfo', None):
        del req.session['AuthorizationInfo']
    
    querydict = dict(req.REQUEST.items())

    try:
        orequest = server.decodeRequest(querydict)
        if hasattr(orequest,'claimed_id') and hasattr(orequest,'identity'):
            if (orequest.claimed_id and orequest.identity) is None:
                response = orequest.answer(allow=False, server_url = orequest.op_endpoint)
                if ('URL/redirect' or 'HTML form') in response.whichEncoding():
                    encoded_response = response.toHTML()
                elif 'kvform' in response.whichEncoding():
                    encoded_response = response.encodeToKVForm()
                return HttpResponseBadRequest(encoded_response)
    except ProtocolError, p:
        if p.whichEncoding() is not None:
            p.whichEncoding()
            if 'URL/redirect' in p.whichEncoding():
                encoded_response = p.toHTML()
            elif 'kvform' in p.whichEncoding():
                encoded_response = p.encodeToKVForm()
            return HttpResponseBadRequest(encoded_response)
        
        elif req.session['OPENID_REQUEST'].message is not None and req.session['OPENID_REQUEST'].message.hasKey('http://specs.openid.net/extensions/pape/1.0','max_auth_age'):
            orequest = cache.get(querydict['openid.claimed_id'])
            cache.delete(querydict['openid.claimed_id'])

            if orequest.mode in ("checkid_immediate", "checkid_setup"):
                if not req.user.is_authenticated():
                    return landing_page(req, orequest)
                openid = openid_is_authorized(req, orequest.identity, orequest.trust_root)
                if openid is not None:
                    oresponse = orequest.answer(True, identity="%s%s" % (
                        host, reverse('openid-provider-identity', args=[openid.openid])))
                elif orequest.immediate:
                    raise Exception('checkid_immediate mode not supported')
            else:
                for k,v in orequest.message.args.iteritems():
                    if v == 'no-encryption' and not req.is_secure():
                        return error_page(req,"Association with no encryption over http is forbidden")
                oresponse = server.handleRequest(orequest)
            webresponse = server.encodeResponse(oresponse)
            req.session['OPENID_REQUEST'] = None
            return django_response(webresponse)

    if not orequest:
        orequest = req.session.get('OPENID_REQUEST', None)
        if not orequest:
            if hasattr(req.user, 'username'):
                return redirect_to(req,'/')
            
            trustedroots = []
            trustroot = []
            openids = {}

            for openid in req.user.openid_set.iterator():
                openids[openid.id] = {'caption':openid.openid}
                openids[openid.id]['trustroot'] = {}
                for trust in openid.trustedroot_set.iterator():
                    openids[openid.id]['trustroot'][trust.id] = trust.trust_root
            
            nb_openid = len(openids)
            
            return render_to_response('django_openid_provider/server.html', {'openids':openids, 'uri':get_base_uri(req), 'oipath':settings.IDPOI_PATH, 'nb_openid':nb_openid},context_instance=RequestContext(req))

        else:
            # remove session stored data:
            del req.session['OPENID_REQUEST']
    
    elif hasattr(orequest,'message'):
        if orequest.message is not None and orequest.message.hasKey('http://specs.openid.net/extensions/pape/1.0','max_auth_age'):
            import time
            delta = time.time() - time.mktime(req.user.last_login.timetuple())
            max_auth = int(orequest.message.getArg('http://specs.openid.net/extensions/pape/1.0','max_auth_age').encode())
    
            if delta > max_auth:
                from django.core.cache import cache
                cache.set(orequest.claimed_id,orequest)
                return landing_page(req, orequest)

    if orequest.mode in ("checkid_immediate", "checkid_setup"):

        if not req.user.is_authenticated():
            return landing_page(req, orequest)

        openid = openid_is_authorized(req, orequest.identity, orequest.trust_root)

        if openid is not None:
            oresponse = orequest.answer(True, identity="%s%s" % (
                host, reverse('openid-provider-identity', args=[openid.openid])))
        elif orequest.immediate:
            raise Exception('checkid_immediate mode not supported')
        else:
            req.session['OPENID_REQUEST'] = orequest
            return HttpResponseRedirect(reverse('openid-provider-decide'))
    else:
        for k,v in orequest.message.args.iteritems():
            if v == 'no-encryption' and not req.is_secure():
                return error_page(req,"Association with no encryption over http is forbidden")
        oresponse = server.handleRequest(orequest)
    webresponse = server.encodeResponse(oresponse)
    return django_response(webresponse)


def openid_is_authorized(req, identity_url, trust_root):
    """
    Check that they own the given identity URL, and that the trust_root is 
    in their whitelist of trusted sites.
    """
    if not req.user.is_authenticated():
        return None

    openid = openid_get_identity(req, identity_url)
    if openid is None:
        return None

    try:
        if openid.trustedroot_set.filter(trust_root=trust_root).count() < 1:
            return None
        elif "openid.return_to" in req.GET.keys(): 
            trust_root_valid = verifyReturnTo(req.GET['openid.realm'], req.GET['openid.return_to']) and "Valid" or "Invalid" 
            realm_str = req.GET['openid.realm']
            return_to = req.GET['openid.return_to']
            if trust_root_valid is "Invalid": 
                return  None
    except:
        pass
    
    return openid

@csrf_exempt
@login_required
def openid_decide(req):
    """
    The page that asks the user if they really want to sign in to the site, and
    lets them add the consumer to their trusted whitelist.
    # If user is logged in, ask if they want to trust this trust_root
    # If they are NOT logged in, show the landing page
    """
    from openid.yadis.discover import DiscoveryFailure
    from openid.fetchers import HTTPFetchingError
    
    orequest = req.session.get('OPENID_REQUEST')
    
    if not req.user.is_authenticated():
        return landing_page(req, orequest)

    openid = openid_get_identity(req, orequest.identity)


    if openid is None:
        return error_page(req, "You are signed in but you don't have OpenID here!")
    if req.method == 'POST' and req.POST.get('decide_page', False) and req.POST.get('allow',False):
        allowed = 'allow' in req.POST
        if openid.trustedroot_set.filter(trust_root=orequest.trust_root).count() < 1:
            openid.trustedroot_set.create(trust_root=orequest.trust_root)
        return HttpResponseRedirect(reverse('openid-provider-root'))
    elif req.method == 'POST' and req.POST.get('cancel',False):
        return HttpResponseRedirect('/')

    try:
        trust_root_valid = verifyReturnTo(orequest.trust_root, orequest.return_to ) and "Valid" or "Invalid"
    except HTTPFetchingError:
        trust_root_valid = "Unreachable"
    except DiscoveryFailure:
        trust_root_valid = "DISCOVERY_FAILED"

    return render_to_response('openid_provider/decide.html', {
            'title': 'Trust this site?',
            'trust_root': orequest.trust_root,
            'trust_root_valid': trust_root_valid,
            'identity': orequest.identity,
        },
        context_instance=RequestContext(req))

@login_required(redirect_field_name = '/')
def manage_trustroot(request):
    trustedroots = []
    trustroot = []
    openids = {}

    for openid in request.user.openid_set.iterator():
        openids[openid.id] = {'caption':openid.openid}
        openids[openid.id]['trustroot'] = {}
        for trust in openid.trustedroot_set.iterator():
            openids[openid.id]['trustroot'][trust.id] = trust.trust_root
    
    trust_sum = 0
    for k, v in openids.iteritems():
        dic = v['trustroot']
        trust_sum += len(dic)

    if request.method == 'POST':
        openids_remove = request.POST.getlist('trustremove')
        
        for openid in request.user.openid_set.iterator():
            for trust in openid.trustedroot_set.iterator():
                if unicode(trust.id) in openids_remove:
                    trust.delete()
        
        return redirect_to(request,'/openid/manage')

    return render_to_response('django_openid_provider/manage_trustroot.html',{'openids':openids,'uri':get_base_uri(request),'oipath':settings.IDPOI_PATH,'trust_sum':trust_sum},context_instance=RequestContext(request))

@login_required(redirect_field_name = '/')
def manage_id(request):

    openids = {}

    for openid in request.user.openid_set.iterator():
        openids[openid.id] = {'caption':openid.openid,'Default':openid.default}
        openids[openid.id]['trustroot'] = {}
        for trust in openid.trustedroot_set.iterator():
            openids[openid.id]['trustroot'][trust.id] = trust.trust_root

    nb_openids = len(openids)

    if request.method == 'POST':
        Id_remove = None
        for k,v in request.POST.iteritems() :
            if v == 'Remove':
                Id_remove = k

        if Id_remove is not None:
            for Id in request.user.openid_set.iterator():
                if unicode(Id_remove) == Id.openid:
                    trust = []
                    for t in Id.trustedroot_set.iterator():
                        trust.append(t.trust_root)
                    return render_to_response('django_openid_provider/manage_id_confirm.html',{'id':Id_remove,'trust':trust},context_instance=RequestContext(request))
        else:
            for k,v in request.POST.iteritems():
                if v == "Make default":
                    Id_default = k
                    for o in request.user.openid_set.iterator():
                        if o.openid == Id_default:
                            o.default = True
                            o.save()
                        elif o.default:
                            o.default = False
                            o.save()
            return redirect_to(request,'/openid/manageid')
    else:
        form = addopenid_form()
        messages = request.user.get_and_delete_messages()
        if len(messages) == 0:
            return render_to_response('django_openid_provider/manage_id.html',{'openids':openids,'form':form,'uri':get_base_uri(request),'oipath':settings.IDPOI_PATH, 'nb_openids':nb_openids},context_instance=RequestContext(request))
        elif len(messages) == 1:
            messages = messages[0].decode()
            return render_to_response('django_openid_provider/manage_id.html',{'openids':openids,'form':form,'uri':get_base_uri(request),'oipath':settings.IDPOI_PATH,'message':messages},context_instance=RequestContext(request))


@login_required
def manage_id_confirm(request):
    if request.method == 'POST' and request.POST['Answer'] == 'Yes':
        Id = request.POST['idremove']
        for Id_remove in request.user.openid_set.iterator():
            if unicode(Id) == Id_remove.openid:
                Id_remove.delete()
                return redirect_to(request,'/openid/manageid')
    return redirect_to(request,'/openid/manageid')


class addopenid_form(forms.Form):
    Default = forms.BooleanField()
    openid = forms.CharField(max_length = 200)

from django.db import IntegrityError
def addopenid(request):
    if request.method == 'POST':
        form = addopenid_form(request.POST)
        openid = request.POST['openid']
        if match(openid): 
            user = request.user
            if 'Default' in form.data.keys() and form.data['Default'] == 'on':
               Default = True
            else:
               Default = False
            try:
                user.openid_set.create(openid = openid, default = Default)
            except IntegrityError:
                msg = openid + ' is already use by someone else please choose another openid identifier'
                request.user.message_set.create(message = msg)
        else:
            if not match(openid):
                msg = "Your OpenID identity can not be " + openid
                request.user.message_set.create(message = msg)
            else:
                request.user.message_set.create(message = 'Your OpenID identity can only contain letters, numbers and underscores')
    return redirect_to(request,'/openid/manageid/')

def match(strg, search = re.compile(r'[^a-z0-9._]').search):
    if res or not bool(search(strg)):
        return False
    else:
        return True
