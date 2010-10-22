from django.contrib.auth.decorators import login_required

@login_required
def consent(request, nonce = '', next = None, provider_id = None):
   '''On a GET produce a form asking for consentment,

       On a POST handle the form and redirect to next'''
   # TODO: implement me
   if not nonce or next or provider_id:
       return Http404()
   raise NotImplementedError('Implement consent')
   # Must set key consent or forbid in the nonce dict

