import collections

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from authentic2.saml.models import LibertyProvider


@login_required
def consent_federation(request, nonce = '', next = None, provider_id = None):
    '''On a GET produce a form asking for consentment,
       On a POST handle the form and redirect to next'''
    if request.method == "GET":
        return render_to_response('interaction/consent_federation.html',
            {'provider_id': request.GET.get('provider_id', ''),
             'nonce': request.GET.get('nonce', ''),
             'next': request.GET.get('next', '')},
            context_instance=RequestContext(request))
    else:
        next = '/'
        if 'next' in request.POST:
            next = request.POST['next']
        if 'accept' in request.POST:
            next = next + '&consent_answer=accepted'
            return HttpResponseRedirect(next)
        else:
            next = next + '&consent_answer=refused'
            return HttpResponseRedirect(next)

@login_required
def consent_attributes(request, nonce = '', next = None, provider_id = None):
    '''On a GET produce a form asking for consentment,
       On a POST handle the form and redirect to next'''
    provider = None
    try:
        provider = LibertyProvider.objects.get(entity_id=request.GET.get('provider_id', ''))
    except:
        pass
    next = '/'

    if request.method == "GET":
        attributes = []
        next = request.GET.get('next', '')
        if 'attributes_to_send' in request.session:
            request.session['attributes_to_send'] = \
                collections.OrderedDict(request.session['attributes_to_send'])
            i = 0
            for key, values in request.session['attributes_to_send'].items():
                name = None
                if type(key) is tuple and len(key) == 3:
                    _, _, name = key
                elif type(key) is tuple and len(key) == 2:
                    name, _, = key
                else:
                    name = key
                if name and values:
                    attributes.append((i, name, values))
                    i = i + 1
            name = request.GET.get('provider_id', '')
            if provider:
                name = provider.name or name
            return render_to_response('interaction/consent_attributes.html',
                {'provider_id': name,
                 'attributes': attributes,
                 'allow_selection': request.session['allow_attributes_selection'],
                 'nonce': request.GET.get('nonce', ''),
                 'next': next},
                context_instance=RequestContext(request))

    elif request.method == "POST":
        if request.session['allow_attributes_selection']:
            vals = \
                [int(value) for key, value in request.POST.items() \
                    if 'attribute_nb' in key]
            attributes_to_send = dict()
            i = 0
            for k, v in request.session['attributes_to_send'].items():
                if i in vals:
                    attributes_to_send[k] = v
                i = i + 1
            request.session['attributes_to_send'] = attributes_to_send
        if 'next' in request.POST:
            next = request.POST['next']
        if 'accept' in request.POST:
            next = next + '&consent_attribute_answer=accepted'
        else:
            next = next + '&consent_attribute_answer=refused'
    return HttpResponseRedirect(next)
