from django.views.decorators.csrf import csrf_exempt
from openid_provider.views import openid_decide as origin_openid_decide
from openid_provider.views import openid_is_authorized
from openid_provider.views import django_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context
from django.views.generic.simple import redirect_to
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from openid.server.server import Server
from django.core.urlresolvers import reverse
import re
from openid_provider.views import get_base_uri
from django.template import RequestContext
import settings

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
    orequest = server.decodeRequest(querydict)
    if not orequest:
        orequest = req.session.get('OPENID_REQUEST', None)
        if not orequest:
            # not request, render info page:
            return render_to_response('openid_provider/server.html',
                {'host': host,},
                context_instance=RequestContext(req))
        else:
            # remove session stored data:
            del req.session['OPENID_REQUEST']
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

@csrf_exempt
def openid_decide(req):
    return origin_openid_decide(req)

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
            

    if request.method == 'POST':
        openids_remove = request.POST.getlist('trustremove')
        
        for openid in request.user.openid_set.iterator():
            for trust in openid.trustedroot_set.iterator():
                if unicode(trust.id) in openids_remove:
                    trust.delete()
        
        return redirect_to(request,'/openid/manage')

    return render_to_response('django_openid_provider/manage_trustroot.html',{'openids':openids,'uri':get_base_uri(request),'oipath':settings.IDPOI_PATH},context_instance=RequestContext(request))

@login_required(redirect_field_name = '/')
def manage_id(request):

    openids = {}

    for openid in request.user.openid_set.iterator():
        openids[openid.id] = {'caption':openid.openid,'Default':openid.default}
        openids[openid.id]['trustroot'] = {}
        for trust in openid.trustedroot_set.iterator():
            openids[openid.id]['trustroot'][trust.id] = trust.trust_root



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

    form = addopenid_form()
    return render_to_response('django_openid_provider/manage_id.html',{'openids':openids,'form':form,'uri':get_base_uri(request),'oipath':settings.IDPOI_PATH},context_instance=RequestContext(request))


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

    
def addopenid(request):
    if request.method == 'POST':
        form = addopenid_form(request.POST)
        openid = request.POST['openid']
        print openid
        if match(openid): 
            user = request.user
            if hasattr(request.POST,'Default'):
               Default = True
            else:
               Default = False
            user.openid_set.create(openid = openid, default = Default)

    return redirect_to(request,'/openid/manageid/')

def match(strg, search = re.compile(r'[^a-z0-9.]').search):
    return not bool(search(strg))
