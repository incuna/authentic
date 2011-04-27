import logging
import random
import datetime
import string

from django.http import HttpResponseRedirect, HttpResponseBadRequest, \
    HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.views import redirect_to_login, logout
from django.utils.http import urlquote, urlencode
from django.conf.urls.defaults import patterns, url
from django.conf import settings

from models import CasTicket
from authentic2.auth2_auth.views import redirect_to_login as \
    auth2_redirect_to_login
import authentic2.auth2_auth.models as auth2_auth_models
from constants import SERVICE_PARAM, RENEW_PARAM, GATEWAY_PARAM, ID_PARAM, \
    CANCEL_PARAM, SERVICE_TICKET_PREFIX, TICKET_PARAM, \
    CAS10_VALIDATION_FAILURE, CAS10_VALIDATION_SUCCESS, PGT_URL_PARAM, \
    INVALID_REQUEST_ERROR, INVALID_TICKET_ERROR, INVALID_SERVICE_ERROR, \
    INTERNAL_ERROR, CAS20_VALIDATION_FAILURE, CAS20_VALIDATION_SUCCESS

logger = logging.getLogger('authentic2.idp.idp_cas')

ALPHABET = string.letters+string.digits+'-'

class CasProvider(object):
    def get_url(self):
        return patterns('cas',
                url('^login$', self.login),
                url('^continue$', self.continue_cas),
                url('^validate$', self.validate),
                url('^serviceValidate$', self.service_validate),
                url('^logout$', self.logout))
    url = property(get_url)

    def make_id(self, prefix='', length=29):
        l = length-len(prefix)
        content = ( random.SystemRandom().choice(ALPHABET) for x in range(l) )
        return prefix + ''.join(content)

    def create_service_ticket(self, service, renew=False, validity=True,
            expire=None, user=None):
        '''Create a fresh service ticket'''
        validity = validity and not renew
        return CasTicket.objects.create(ticket_id=self.make_id(prefix='ST-'),
            service=service,
            renew=renew,
            validity=validity,
            expire=None,
            user=user)

    def check_authentication(self, request, st):
        '''
           Check that the given service ticket is linked to an authentication
           event.
        '''
        return False

    def failure(self, request, reason):
        '''
           Return a HTTP 400 code with the @reason argument as content.
        '''
        return HttpResponseBadRequest(content=reason)

    def login(self, request):
        if request.method != 'GET':
            return HttpResponseBadRequest('Only GET HTTP verb is accepted')
        service = request.GET.get(SERVICE_PARAM)
        renew = request.GET.get(RENEW_PARAM) is not None
        gateway = request.GET.get(GATEWAY_PARAM) is not None

        if not service:
            return self.failure(request, 'no service field')
        if not service.startswith('http://') and not \
                service.startswith('https://'):
            return self.failure(request, 'service is not an HTTP or HTTPS URL')
        return self.handle_login(request, service, renew, gateway)

    def must_authenticate(self, request, renew):
        '''Does the user needs to authenticate ?

           You can refer to the current request and to the renew parameter from
           the login reuest.

           Returns a boolean.
        '''
        return not request.user.is_authenticated() or renew

    def get_cas_user(self, request):
        '''Return an ascii string representing the user.

           It should usually be the uid from an user record in a LDAP
        '''
        return request.user.username

    def handle_login(self, request, service, renew, gateway, duration=None):
        '''
           Handle a login request

           @service: URL where the CAS ticket will be returned
           @renew: whether to re-authenticate the user
           @gateway: do not let the IdP interact with the user

           It is an extension point
        '''
        logger.debug('Handling CAS login for service:%r with parameters \
renew:%s and gateway:%s' % (service, renew, gateway))

        if duration is None or duration < 0:
            duration = 5*60
        if duration:
            expire = datetime.datetime.now() + \
                datetime.timedelta(seconds=duration)
        else:
            expire = None
        if self.must_authenticate(request, renew):
            st = self.create_service_ticket(service, validity=False,
                    renew=renew, expire=expire)
            return self.authenticate(request, st, passive=gateway)
        else:
            st = self.create_service_ticket(service, expire=expire,
                    user=self.get_cas_user(request))
            return self.handle_login_after_authentication(request, st)

    def cas_failure(self, request, st, reason):
        logger.debug('%s, redirecting without ticket to %r' % (reason, \
            st.service))
        st.delete()
        return HttpResponseRedirect(st.service)

    def authenticate(self, request, st, passive=False):
        '''
           Redirect to an login page, pass a cookie to the login page to
           associate the login event with the service ticket, if renew was
           asked

           It is an extension point. If your application support some passive
           authentication, it must be tried here instead of failing.
           @request: current django request
           @st: a currently invalid service ticket
           @passive: whether we can interact with the user
        '''

        if passive:
            return self.cas_failure(request, st,
                    'user needs to log in and gateway is True')
        if st.renew:
            raise NotImplementedError('renew is not implemented')
        return redirect_to_login(next='%s?id=%s' % (reverse(self.continue_cas),
                urlquote(st.ticket_id)))

    def continue_cas(self, request):
        '''Continue CAS login after authentication'''
        ticket_id = request.GET.get(ID_PARAM)
        cancel = request.GET.get(CANCEL_PARAM) is not None
        if ticket_id is None:
            return self.failure(request, 'missing ticket id')
        if not ticket_id.startswith(SERVICE_TICKET_PREFIX):
            return self.failure(request, 'invalid ticket id')
        try:
            st = CasTicket.objects.get(ticket_id=ticket_id)
        except CasTicket.DoesNotExist:
            return self.failure(request, 'unknown ticket id')
        if cancel:
            return self.cas_failure(request, st, 'login cancelled')
        if st.renew:
            # renew login
            if self.check_authentication(request, st):
                return self.handle_login_after_authentication(request, st)
            else:
                return self.authenticate(request, st)
        elif self.must_authenticate(request, False):
            # not logged ? Yeah do it again!
            return self.authenticate(request, st)
        else:
            # normal login
            st.user = self.get_cas_user(request)
            st.validity = True
            st.save()
        return self.handle_login_after_authentication(request, st)

    def handle_login_after_authentication(self, request, st):
        if not st.valid():
            return self.cas_failure(request, st,
                    'service ticket id is not valid')
        else:
            return self.return_ticket(request, st)

    def return_ticket(self, request, st):
        return HttpResponseRedirect('%s?ticket=%s' % (st.service,
            st.ticket_id))

    def validate(self, request):
        if request.method != 'GET':
            return self.failure(request, 'Only GET HTTP verb is accepted')
        service = request.GET.get(SERVICE_PARAM)
        ticket = request.GET.get(TICKET_PARAM)
        renew = request.GET.get(RENEW_PARAM) is not None
        if service is None:
            return self.failure(request, 'service parameter is missing')
        if service is None:
            return self.failure(request, 'ticket parameter is missing')
        if not ticket.startswith(SERVICE_TICKET_PREFIX):
            return self.failure(request, 'invalid ticket prefix')
        try:
            st = CasTicket.objects.get(ticket_id=ticket)
            st.delete()
        except CasTicket.DoesNotExist:
            st = None
        if st is None \
                or not st.valid() \
                or (st.renew ^ renew) \
                or st.service != service:
            return HttpResponse(CAS10_VALIDATION_FAILURE)
        else:
            return HttpResponse(CAS10_VALIDATION_SUCCESS % st.user)

    def get_cas20_error_message(self, code):
        return '' # FIXME

    def cas20_error(self, request, code):
        message = self.get_cas20_error_message(code)
        return HttpResponse(CAS20_VALIDATION_FAILURE % (code, message))

    def service_validate(self, request):
        '''
           CAS 2.0 serviceValidate endpoint.
        '''
        try:
            if request.method != 'GET':
                return self.failure('Only GET HTTP verb is accepted')
            service = request.GET.get(SERVICE_PARAM)
            ticket = request.GET.get(TICKET_PARAM)
            renew = request.GET.get(RENEW_PARAM) is not None
            pgt_url = request.GET.get(PGT_URL_PARAM)
            if service is None:
                return self.cas20_error(request, INVALID_REQUEST_ERROR)
            if service is None:
                return self.cas20_error(request, INVALID_REQUEST_ERROR)
            if not ticket.startswith(SERVICE_TICKET_PREFIX):
                return self.cas20_error(request, INVALID_TICKET_ERROR)
            try:
                st = CasTicket.objects.get(ticket_id=ticket)
                st.delete()
            except CasTicket.DoesNotExist:
                st = None
            if st is None \
                    or not st.valid() \
                    or (st.renew ^ renew):
                return self.cas20_error(request, INVALID_TICKET_ERROR)
            if st.service != service:
                return self.cas20_error(request, INVALID_SERVICE_ERROR)
            if pgt_url:
                raise NotImplementedError(
                        'CAS 2.0 pgtUrl parameter is not handled')
            return HttpResponse(CAS20_VALIDATION_SUCCESS % st.user)
        except Exception:
            return self.cas20_error(INTERNAL_ERROR)

    def logout(self, request):
        next = request.GET.get('url')
        return logout(request, next_page=next)

class Authentic2CasProvider(CasProvider):
    def authenticate(self, request, st, passive=False):
        next = '%s?id=%s' % (reverse(self.continue_cas),
                urlquote(st.ticket_id))
        if passive:
            if getattr(settings, 'AUTH_SSL', False):
                query = { 'next': next,
                    'nonce': st.ticket_id }
                return HttpResponseRedirect('%s?%s' %
                        (reverse('user_signin_ssl'), urlencode(query)))
            else:
                return self.cas_failure(request, st, 
                    '''user needs to login and no passive authentication \
is possible''')
        return auth2_redirect_to_login(request, next=next, nonce=st.ticket_id)

    def check_authentication(self, request, st):
        try:
            ae = auth2_auth_models.AuthenticationEvent.objects \
                    .get(nonce=st.ticket_id)
            st.user = ae.who
            st.validity = True
            st.save()
            return True
        except auth2_auth_models.AuthenticationEvent.DoesNotExist:
            return False
