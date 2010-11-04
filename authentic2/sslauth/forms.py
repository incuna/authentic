import django.forms as forms
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.utils.translation import ugettext_lazy as _

from models import ClientCertificate, DistinguishedName
from util import SSLInfo

# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.
attrs_dict = { 'class': 'required' }

class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.
    
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    
    Subclasses should feel free to add any additional validation they
    need, but should either preserve the base ``save()`` or implement
    a ``save()`` which accepts the ``profile_callback`` keyword
    argument and passes it through to
    ``RegistrationProfile.objects.create_inactive_user()``.
    
    """
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'username'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_(u'email address'))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        forms.Form.__init__(self, *args, **kwargs)

    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_(u'This username is already taken. Please choose another.'))

    def save(self, profile_callback=None):
        """
        Create the new ``User`` and ``RegistrationProfile``, and
        returns the ``User``.
        
        This is essentially a light wrapper around
        ``RegistrationProfile.objects.create_inactive_user()``,
        feeding it the form data and a profile callback (see the
        documentation on ``create_inactive_user()`` for details) if
        supplied.
        
        """
        ssl_info = SSLInfo(self.request)
        if not ssl_info.cert:
            raise ValueError('Missing cert')
        new_user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'])
        new_user.backend = 'authentic2.sslauth.backends.SSLAuthBackend'
        cert = ClientCertificate()
        cert.user = new_user
        cert.cert = ssl_info.cert
        cert.save()
        # Automatically log in the new user
        login(self.request, new_user)
        print 'ok', new_user
        return new_user
