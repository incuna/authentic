from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm

attrs_dict = { 'class': 'required' }

class AuthenticRegistrationForm(RegistrationForm):
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'username'),
                                error_messages = {'invalid': _(u'your username must contain only letters, numbers and no spaces')})

