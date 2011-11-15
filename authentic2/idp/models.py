import lasso

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _


from authentic2.attribute_aggregator.mapping import ATTRIBUTE_MAPPING, \
    ATTRIBUTE_NAMESPACES

from authentic2.attribute_aggregator.models import AttributeSource


ATTRIBUTES = [(key, key) \
    for key in sorted(ATTRIBUTE_MAPPING.iterkeys())]
ATTRIBUTES_NS = [('Default', 'Default')] \
    + [(ns, ns) for ns in ATTRIBUTE_NAMESPACES]

ATTRIBUTE_VALUE_FORMATS = (
        (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_URI, 'SAMLv2 URI'),
        (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC, 'SAMLv2 BASIC'))


def set_user_consent_attributes(user, provider, attributes):
    if not user or not provider:
        return None
    return UserConsentAttributes.objects.get_or_create(user=user,
        object_id=provider.id,
             content_type=ContentType.objects.get_for_model(provider))


def get_user_consent_attributes(user, provider, attributes):
    if not user or not provider:
        return None
    try:
        return UserConsentAttributes.objects.get(user=user,
            object_id=provider.id,
            content_type=ContentType.objects.get_for_model(provider),
            attributes=attributes)
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
        return ('profiles_profile_detail', (),
            {'username': self.user.username})
    get_absolute_url = models.permalink(get_absolute_url)


class AttributeItem(models.Model):
    attribute_name = models.CharField(max_length = 100, choices = ATTRIBUTES,
        default = ATTRIBUTES[0])
    # ATTRIBUTE_VALUE_FORMATS[0] =>
    #    (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC, 'SAMLv2 BASIC')
    output_name_format = models.CharField(max_length = 100,
        choices = ATTRIBUTE_VALUE_FORMATS,
        default = ATTRIBUTE_VALUE_FORMATS[0])
    #ATTRIBUTES_NS[0] => ('Default', 'Default')
    output_namespace = models.CharField(max_length = 100,
        choices = ATTRIBUTES_NS, default = ATTRIBUTES_NS[0])
    required = models.BooleanField(default=False)
    source = models.ForeignKey(AttributeSource, blank = True, null = True)

    class Meta:
        verbose_name = _('attribute of a list (SSO Login)')
        verbose_name_plural = _('attributes of lists (SSO Login)')

    def __unicode__(self):
        s = self.attribute_name
        s += ' (Output name fomat: %s)' % self.output_name_format
        s += ' (Output namespace: %s)' % self.output_namespace
        s += ' (Required: %s)' % self.required
        s += ' (Source: %s)' % self.source
        return s


class AttributeList(models.Model):
    name = models.CharField(max_length = 100, unique = True)
    attributes = models.ManyToManyField(AttributeItem,
        related_name = "attributes of the list",
        blank = True, null = True)

    class Meta:
        verbose_name = _('attribute list (SSO Login)')
        verbose_name_plural = _('attribute lists (SSO Login)')

    def __unicode__(self):
        return self.name


class AttributePolicy(models.Model):
    name = models.CharField(max_length = 100, unique = True)
    enabled = models.BooleanField(verbose_name = _('Enabled'))
    # List of attributes to provide from pull sources at SSO Login.
    # If an attribute is indicate without a source, from any source.
    # The output format and namespace is given by each attribute.
    attribute_list_for_sso_from_pull_sources = \
        models.ForeignKey(AttributeList,
        related_name = "attributes from pull sources",
        blank = True, null = True)

    # Set to true for proxying attributes from pull sources at SSO Login.
    # Attributes are in session.
    # All attributes are forwarded as is except if the parameter
    # 'map_attributes_from_push_sources' is initialized
    forward_attributes_from_push_sources = models.BooleanField(default=False)

    # Map attributes in session
    # forward_attributes_in_session must be true
    # At False, all attributes are forwarded as is
    # At true, look for the namespace of the source for input, If not found,
    # system namespace. Look for the options attribute_name_format and
    # output_namespace of the attribute policy for output.
    map_attributes_from_push_sources = models.BooleanField(default=False)

    # ATTRIBUTE_VALUE_FORMATS[0] =>
    #    (lasso.SAML2_ATTRIBUTE_NAME_FORMAT_BASIC, 'SAMLv2 BASIC')
    output_name_format = models.CharField(max_length = 100,
        choices = ATTRIBUTE_VALUE_FORMATS,
        default = ATTRIBUTE_VALUE_FORMATS[0])

    #ATTRIBUTES_NS[0] => ('Default', 'Default')
    output_namespace = models.CharField(max_length = 100,
        choices = ATTRIBUTES_NS, default = ATTRIBUTES_NS[0])

    # Filter attributes pushed from source.
    source_filter_for_sso_from_push_sources = \
        models.ManyToManyField(AttributeSource,
        related_name = "filter attributes of push sources with sources",
        blank = True, null = True)

    # List of attributes to filter from pull sources at SSO Login.
    attribute_filter_for_sso_from_push_sources = \
        models.ForeignKey(AttributeList,
        related_name = "filter attributes of push sources with list",
        blank = True, null = True)

    # The sources of attributes of the previous list are considered.
    # May be used conjointly with 'source_filter_for_sso_from_push_sources'
    filter_source_of_filtered_attributes = models.BooleanField(default=False)

    # To map the attributes of forwarded attributes with the defaut output
    # format and namespace, use 'map_attributes_from_pull_sources'
    # Use the following option to use the output format and namespace
    # indicated for each attribute.
    map_attributes_of_filtered_attributes = models.BooleanField(default=False)


    # Set to true to take in account missing required attributes
    send_error_and_no_attrs_if_missing_required_attrs = \
        models.BooleanField(default=False)

    # Ask user consent
    #ask_user_consent = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('attribute options policy')
        verbose_name_plural = _('attribute options policies')

    def __unicode__(self):
        from authentic2.saml.models import LibertyProvider
        names = []
        for sp in LibertyProvider.objects.all():
            try:
                if sp.service_provider.attribute_policy.id == self.id:
                    names.append(sp.name)
            except:
                pass
        l = ', '.join(names)
        if l:
            return '%s associated with %s' % (self.name, l)
        return '%s not yet associated with a service provider' % self.name


def get_attribute_policy(provider):
    try:
        return AttributePolicy.objects.get(name='All', enabled=True)
    except AttributePolicy.DoesNotExist:
        pass
    try:
        if provider.service_provider.enable_following_attribute_policy:
            if provider.service_provider.attribute_policy:
                return provider.service_provider.attribute_policy
    except:
        pass
    try:
        return AttributePolicy.objects.get(name='Default', enabled=True)
    except AttributePolicy.DoesNotExist:
        pass
    return None
