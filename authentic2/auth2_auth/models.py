from datetime import date, timedelta

from django.db import models
from django.utils.translation import ugettext as _
from django.conf import settings

class AuthenticationEventManager(models.Manager):
    def cleanup(self):
        expire = getattr(settings, 'AUTHENTICATION_EVENT_EXPIRATION',
                3600*24*7)
        self.filter(when__lt=date.today()-timedelta(seconds=expire)).delete()

class AuthenticationEvent(models.Model):
    '''Record authentication events whatever the source'''
    when = models.DateTimeField(auto_now = True)
    who = models.CharField(max_length = 80)
    how = models.CharField(max_length = 10)
    nonce = models.CharField(max_length = 255)

    objects = AuthenticationEventManager()

    def __unicode__(self):
        return _('Authentication of %(who)s by %(how)s at %(when)s') % \
            self.__dict__
