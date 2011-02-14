from django.db import models
from django.utils.translation import ugettext as _

class AuthenticationEvent(models.Model):
    '''Record authentication events whatever the source'''
    when = models.DateTimeField(auto_now = True)
    who = models.CharField(max_length = 80)
    how = models.CharField(max_length = 10)
    nonce = models.CharField(max_length = 255)

    def __unicode__(self):
        return _('Authentication of %(who)s by %(how)s at %(when)s') % self.__dict__
