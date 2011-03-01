from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

@login_required
def consent(request, nonce = '', next = None, provider_id = None):
    '''On a GET produce a form asking for consentment,

       On a POST handle the form and redirect to next'''
    if request.method == "GET":
        attributes = []
        import sys
        print >> sys.stderr, "request.session.has_key('attributes_to_send') " + str(request.session['attributes_to_send'])
        if request.session.has_key('attributes_to_send'):
            attrs = request.session['attributes_to_send']
            for key in attrs:
                name = None
                if type(key) is tuple and len(key) == 2:
                    name, format = key
                elif type(key) is tuple:
                    return
                else:
                    name = key
                v = name + ' '
                print >> sys.stderr, "v " + v
                values = attrs[key]
                for value in values:
                    if value is True:
                        value = 'true'
                    elif value is False:
                        value = 'false'
                    else:
                        value = str(value)
                    if type(value) is unicode:
                        value = value.encode('utf-8')
                    #else:
                    #    value = sitecharset2utf8(value)
                    v += value + ' '
                print >> sys.stderr, "v " + v
                attributes.append(v)
                print >> sys.stderr, "attributes " + str(attributes)

        return render_to_response('interaction/consent.html',
            {'provider_id': request.GET.get('provider_id', ''),
             'attributes': attributes,
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
