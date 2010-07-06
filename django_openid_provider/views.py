from django.views.decorators.csrf import csrf_exempt
from openid_provider.views import openid_decide as origin_openid_decide
from openid_provider.views import openid_server as origin_openid_server
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.views.generic.simple import redirect_to
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
import re
from openid_provider.views import get_base_uri
import settings

@csrf_exempt
def openid_server(req):
    return origin_openid_server(req)

@csrf_exempt
def openid_decide(req):
    return origin_openid_decide(req)

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
                    template = get_template('django_openid_provider/manage_id_confirm.html')
                    html = template.render(Context({'id':Id_remove,'trust':trust}))
                    return HttpResponse(html)
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
    return render_to_response('django_openid_provider/manage_id.html',{'openids':openids,'form':form,'uri':get_base_uri(request),'oipath':settings.IDPOI_PATH})


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
