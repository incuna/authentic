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

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    first_name = models.CharField(_('first name'),
            max_length=30,
            blank=True)
    last_name = models.CharField(_('last name'),
            max_length=30,
            blank=True)
    email = models.EmailField(_('e-mail address'), blank=True)
    nickname = models.CharField(_('nickname'), max_length=50, blank=True)
    url = models.URLField("Website", blank=True)
    company = models.CharField(verbose_name=_("Company"),
            max_length=50, blank=True)
    phone = models.CharField(verbose_name=_("Phone"),
            max_length=50, blank=True)
    postal_address = models.TextField(verbose_name=_("Postal address"),
            max_length=255, blank=True)

    def save(self):
        # Synchronize with user object
        self.user.first_name = self.first_name
        self.user.last_name = self.last_name
        self.user.save()
        # TODO: synchronize email
        super(UserProfile, self).save()

    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })
    get_absolute_url = models.permalink(get_absolute_url)
