import datetime as dt

from django.db import models

__all__ = ('Nonce',)

_NONCE_LENGTH_CONSTANT = 256

class NonceManager(models.Manager):
    def cleanup(self, now=None):
        now = now or dt.datetime.now()
        self.filter(not_on_or_after__lt=now).delete()

class Nonce(models.Model):
    value = models.CharField(max_length=_NONCE_LENGTH_CONSTANT)
    context = models.CharField(max_length=_NONCE_LENGTH_CONSTANT, blank=True,
            null=True)
    not_on_or_after = models.DateTimeField(blank=True, null=True)

    objects  = NonceManager()

    def __unicode__(self):
        return self.value
