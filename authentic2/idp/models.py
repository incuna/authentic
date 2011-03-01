from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

def set_user_consent_attributes(user, provider, attributes):
    if not user or not provider:
        return None
    return UserConsentAttributes.objects.get_or_create(user=user, object_id=provider.id,
             content_type=ContentType.objects.get_for_model(provider))

def get_user_consent_attributes(user, provider, attributes):
    if not user or not provider:
        return None
    try:
        return UserConsentAttributes.objects.get(user=user, object_id=provider.id,
             content_type=ContentType.objects.get_for_model(provider), attributes=attributes)
    except:
        return None

class UserConsentAttributes(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    provider = generic.GenericForeignKey('content_type', 'object_id')
    attributes = models.TextField()

    class Meta:
        verbose_name = _('User consent for attributes propagation')

    def __unicode__(self):
        return "User consent for attributes propagation"
