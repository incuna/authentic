from django.template import RequestContext
from django.shortcuts import render_to_response

REGISTERED_SERVICE_LIST = []

def register_service_list(list_or_callable):
    '''Register a list of tuple (uri, name) to present in user service list, or
       a callable which will receive the request object and return a list of tuples.
    '''
    REGISTERED_SERVICE_LIST.append(list_or_callable)

def service_list(request):
    '''Compute the service list to show on user homepage'''
    list = []
    for list_or_callable in REGISTERED_SERVICE_LIST:
        if callable(list_or_callable):
            list += list_or_callable(request)
        else:
            list += list_or_callable
    return list

def homepage(request):
    '''Homepage of the IdP'''
    return render_to_response('index.html',
            { 'authorized_services' : service_list(request) },
            RequestContext(request))
