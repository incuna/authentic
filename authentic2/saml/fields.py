try:
    import cPickle as pickle
except ImportError:
    import pickle

from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import capfirst



# This is a copy of http://djangosnippets.org/snippets/513/
#
# A field which can store any pickleable object in the database. It is
# database-agnostic, and should work with any database backend you can throw at
# it.
#
# Pass in any object and it will be automagically converted behind the scenes,
# and you never have to manually pickle or unpickle anything. Also works fine
# when querying.
#
# Initial author: Oliver Beattie

class PickledObject(str):
    """A subclass of string so it can be told whether a string is
       a pickled object or not (if the object is an instance of this class
       then it must [well, should] be a pickled one)."""
    pass

class PickledObjectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, PickledObject):
            # If the value is a definite pickle; and an error is raised in
            # de-pickling it should be allowed to propogate.
            return pickle.loads(str(value))
        else:
            try:
                return pickle.loads(str(value))
            except:
                # If an error was raised, just return the plain value
                return value

    def get_db_prep_save(self, value, connection):
        if value is not None and not isinstance(value, PickledObject):
            value = PickledObject(pickle.dumps(value))
        return value

    def get_internal_type(self):
        return 'TextField'

    def value_to_string(self, obj):
	return PickledObject(pickle.dumps(obj))

    def get_db_prep_lookup(self, lookup_type, value, connection,
            prepared=False):
        if lookup_type == 'exact':
            value = self.get_db_prep_save(value, connection)
            return super(PickledObjectField, self) \
                    .get_db_prep_lookup(lookup_type, value, connection,
                            prepared=prepared)
        elif lookup_type == 'in':
            value = [self.get_db_prep_save(v, connection) for v in value]
            return super(PickledObjectField, self) \
                    .get_db_prep_lookup(lookup_type, value, connection,
                            prepared=prepared)
        else:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)

# This is a modified copy of http://djangosnippets.org/snippets/1200/
#
# We added a validate method.
#
# Usually you want to store multiple choices as a manytomany link to another
# table. Sometimes however it is useful to store them in the model itself. This
# field implements a model field and an accompanying formfield to store multiple
# choices as a comma-separated list of values, using the normal CHOICES
# attribute.
#
# You'll need to set maxlength long enough to cope with the maximum number of
# choices, plus a comma for each.
#
# The normal get_FOO_display() method returns a comma-delimited string of the
# expanded values of the selected choices.
#
# The formfield takes an optional max_choices parameter to validate a maximum
# number of choices.
#
# Initial author: Daniel Roseman

class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        if value and self.max_choices and len(value) > self.max_choices:
            raise forms.ValidationError('You must select a maximum of %s choice%s.'
                    % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value

class MultiSelectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name),
                    'help_text': self.help_text, 'choices':self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def validate(self, value, model_instance):
        out = set()
        if self.choices:
            out |= set([option_key for option_key,_ in self.choices])
        out = set(value)-out
        if out:
            raise ValidationError(self.error_messages['invalid_choice'] % ','.join(list(out)))
        if not value and not self.blank:
            raise ValidationError(self.error_messages['blank'])

    def to_python(self, value):
        if isinstance(value, list):
            return value
        return value.split(",")

    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choicedict = dict(self.choices):",".join([choicedict.get(value,value) for value in getattr(self,fieldname)])
            setattr(cls, 'get_%s_display' % self.name, func)

try:
    # Let South handle our custom fields
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^authentic2\.saml\.fields\."])
except ImportError:
    pass
