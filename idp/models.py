from django.db import models

class AuthenticationEvent(models.Model):
    '''Record authentication events whatever the source'''
    when = models.DateTimeField(auto_now = True)
    who = models.CharField(max_length = 80)
    how = models.CharField(max_length = 10)
    nonce = models.CharField(max_length = 20)
