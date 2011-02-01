import logging

import models
import authentic2.vendor.oath.hotp as hotp
from django.contrib.auth.models import User
from django.db import transaction

logger = logging.getLogger('authentic.auth.auth2_oath')

class OATHTOTPBackend:

    support_oath_otp = True

    @transaction.commit_on_success()
    def authenticate(self, username, oath_otp, format='dec6'):
        '''Lookup the TOTP or HOTP secret for the user and try to authenticate
           the proposed OTP using it.
        '''
        try:
            secret = models.OATHTOTPSecret.objects.get(user__username=username)
        except models.OATHTOTPSecret.DoesNotExist:
            return None
        try:
            accepted, drift = hotp.accept_totp(secret.key, oath_otp, format=format)
        except Exception, e:
            logger.exception('hotp.accept_totp raised', e)
            raise

        if accepted:
            secret.drift = drift
            return User.objects.get(username=username)
        else:
            return None

    def get_user(self, user_id):
        """
        simply return the user object. That way, we only need top look-up the 
        certificate once, when loggin in
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def setup_totp(self, user):
        '''Create a model containing a TOTP secret for the given user and the
           current time drift which initially is zero
        '''
        pass
