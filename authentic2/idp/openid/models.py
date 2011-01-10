# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 : */

import datetime
import time
import calendar

import openid.association
import openid.store.nonce
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User

from authentic2.saml.fields import PickledObjectField

class OpenID(models.Model):
    user = models.ForeignKey(User)
    openid = models.CharField(max_length=200, blank=True, unique=True)
    default = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('OpenID')
        verbose_name_plural = _('OpenIDs')
        ordering = ['openid']

    def __unicode__(self):
        return u"%s|%s" % (self.user.username, self.openid)

    def save(self, *args, **kwargs):
        if self.openid in ['', u'', None]:
            from hashlib import sha1
            import random, base64
            sha = sha1()
            sha.update(unicode(self.user.username).encode('utf-8'))
            sha.update(str(random.random()))
            value = str(base64.b64encode(sha.digest()))
            value = value.replace('/', '').replace('+', '').replace('=', '')
            self.openid = value
        super(OpenID, self).save(*args, **kwargs)
        if self.default:
            self.user.openid_set.exclude(pk=self.pk).update(default=False)

class TrustedRoot(models.Model):
    openid = models.ForeignKey(OpenID)
    trust_root = models.CharField(max_length=200)

    def __unicode__(self):
        return unicode(self.trust_root)

class Association(models.Model):
    server_url = models.CharField(max_length=2047, blank=False)
    handle = models.CharField(max_length=255, blank=False)
    secret = PickledObjectField()
    issued = models.DateTimeField(auto_now_add=True,
            verbose_name="Issue time for this association, as seconds since EPOCH")
    lifetime = models.IntegerField(
            verbose_name="Lifetime of this association as seconds since the issued time")
    expire = models.DateTimeField("After this time, the association will be expired")
    assoc_type = models.CharField(max_length=64, blank=False)

    class Meta:
        unique_together = ('server_url', 'handle')

    def save(self, *args, **kwargs):
        '''Overload default save() method to compute the expire field'''
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
            filter = cls.objects.filter(server_url=server_url, expire__gt=datetime.utcnow())
            if handle is not None:
                filter = filter.filter(handle=handle)
            return fitler.latest('issued').to_association()
        except cls.DoesNotExit:
            return None

    @classmethod
    def cleanup_associations(cls):
        filter = cls.objects.filter(expire__lt=datetime.utcnow())
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

class Nonce(models.Model):
    salt = models.CharField(max_length=40)
    server_url = models.CharField(max_length=2047)
    timestamp = models.IntegerField()

    class Meta:
        unique_together = ('server_url', 'salt')

    @classmethod
    def use_nonce(cls, server_url, timestamp, salt):
        now = time.time()
        if timestamp > now or timestamp + openid.store.nonce.SKEW < now:
            return False

        n, created = cls.objects.get_or_create(server_url=server_url, salt=salt)
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
