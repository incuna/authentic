from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

@login_required
def consent(request, nonce = '', next = None, provider_id = None):
    '''On a GET produce a form asking for consentment,

       On a POST handle the form and redirect to next'''
    if request.method == "GET":
        return render_to_response('interaction/consent.html',
            {'provider_id': request.GET.get('provider_id', ''),
             'nonce': request.GET.get('nonce', ''),
             'next': request.GET.get('next', '')},
            context_instance=RequestContext(request))
    else:
        next = '/'
        if request.POST.has_key('next'):
            next = request.POST['next']
        if request.POST.has_key('accept'):
            next = next + '&consent_answer=accepted'
            return HttpResponseRedirect(next)
        else:
            next = next + '&consent_answer=refused'
            return HttpResponseRedirect(next)
