import lasso
from django.contrib.auth.decorators import login_required

def get_post_saml_request(request):
    '''Return a SAML 1.1 request transmitted through a POST request'''
    return request.POST.get('LAREQ')

@login_required
def sso(request):
    """Endpoint for AuthnRequests asynchronously sent, i.e. POST or Redirect"""
    # 1. Process the request, separate POST and GET treatment
    if request.method == 'GET':
        message = request.META.get('QUERY_STRING')
    elif request.method == 'POST':
        message = get_post_saml_request(request)


    # 2. Lookup the ProviderID

    # 3. Check for permission

    # 3. Build and assertion, fill attributes

    # 3. Depending on the requested profile finish with an artifact or a
    # POST
