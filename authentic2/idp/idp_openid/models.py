# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 : */

import datetime
import time
import calendar

import openid.association
import openid.store.nonce
from django.db import models

from authentic2.saml.fields import PickledObjectField

class TrustedRoot(models.Model):
    user = models.CharField(max_length=255)
    trust_root = models.CharField(max_length=200)
    choices = PickledObjectField()

    def __unicode__(self):
        return unicode(self.trust_root)

class Association(models.Model):
    server_url = models.CharField(max_length=2047, blank=False)
    handle = models.CharField(max_length=255, blank=False)
    secret = PickledObjectField(editable=False)
    issued = models.DateTimeField(editable=False,
            verbose_name="Issue time for this association, as seconds \
since EPOCH")
    lifetime = models.IntegerField(
            verbose_name="Lifetime of this association as seconds since \
the issued time")
    expire = models.DateTimeField("After this time, the association will \
be expired")
    assoc_type = models.CharField(max_length=64, blank=False)

    class Meta:
        unique_together = ('server_url', 'handle')

    def save(self, *args, **kwargs):
        '''Overload default save() method to compute the expire field'''
        self.issued = datetime.datetime.today()
        self.expire = self.issued + datetime.timedelta(seconds=self.lifetime)
        super(Association, self).save(*args, **kwargs)

    def to_association(self):
        '''Convert a model instance to an Association object of the openid
           library.
        '''
        return openid.association.Association(handle=self.handle,
                secret=self.secret,
                issued=calendar.timegm(self.issued.utctimetuple()),
                lifetime=self.lifetime,
                assoc_type=self.assoc_type)

    @classmethod
    def get_association(cls, server_url, handle=None):
        try:
            filter = cls.objects.filter(server_url=server_url,
                expire__gt=datetime.datetime.utcnow())
            if handle is not None:
                filter = filter.filter(handle=handle)
            return filter.latest('issued').to_association()
        except cls.DoesNotExist:
            return None

    @classmethod
    def cleanup_associations(cls):
        filter = cls.objects.filter(expire__lt=datetime.datetime.utcnow())
        count = filter.count()
        filter.delete()
        return count

    @classmethod
    def remove_association(cls, server_url, handle=None):
        filter = cls.objects.filter(server_url=server_url)
        if handle is not None:
            filter = filter.filter(handle=handle)
        filter.delete()

    @classmethod
    def store_association(cls, server_url, association):
        Association(server_url=server_url,
                handle=association.handle,
                secret=association.secret,
                issued=datetime.datetime.utcfromtimestamp(association.issued),
                lifetime=association.lifetime,
                assoc_type=association.assoc_type).save()

class NonceManager(models.Manager):
    def cleanup(self):
        expire = openid.store.nonce.SKEW
        now = calendar.timegm(datetime.datetime.now().utctimetuple())
        self.filter(timestamp__lt=now-expire).delete()

class Nonce(models.Model):
    salt = models.CharField(max_length=40)
    server_url = models.CharField(max_length=2047)
    timestamp = models.IntegerField()

    objects = NonceManager()

    class Meta:
        unique_together = ('server_url', 'salt')

    @classmethod
    def use_nonce(cls, server_url, timestamp, salt):
        now = time.time()
        if timestamp > now or timestamp + openid.store.nonce.SKEW < now:
            return False

        n, created = cls.objects.get_or_create(server_url=server_url,
                salt=salt)
        if created:
            n.timestamp = timestamp
            n.save()
        return created

    @classmethod
    def cleanup_nonces(cls):
        filter = cls.objects.filter(
                timestamp_lt=time.time()-openid.store.nonce.SKEW)
        count = filter.count()
        filter.delete()
        return count
