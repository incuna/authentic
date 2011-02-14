from django.db import models

from datetime import datetime, timedelta

class CasTicketManager(models.Manager):
    def clean_expired(self):
        '''
           Remove expired tickets.
        '''
        self.filter(expire__gte=datetime.now()).delete()

class CasTicket(models.Model):
    '''Session ticket with a CAS 1.0 or 2.0 consumer'''

    ticket_id  = models.CharField(max_length=64)
    renew   = models.BooleanField(default=False)
    validity   = models.BooleanField(default=False)
    service = models.CharField(max_length=256)
    user    = models.CharField(max_length=128,blank=True,null=True)
    creation = models.DateTimeField(auto_now_add=True)
    '''Duration length for the ticket as seconds'''
    expire = models.DateTimeField(blank=True, null=True)

    def valid(self):
        return self.validity and not self.expired()

    def expired(self):
        '''Check if the given CAS ticket has expired'''
        if self.expire:
            return datetime.now() >= self.expire
        else:
            return False
