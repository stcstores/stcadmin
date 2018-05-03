"""Base classes for product fields."""

from inspect import isclass

from django import forms
from django.core.exceptions import ValidationError

from inventory.forms import widgets


class Validators:
    """Holder class for validation methods."""

    @staticmethod
    def alphanumeric(value):
        """Validate every character in value is alphanumeric."""
        if isinstance(value, list):
            for v in value:
                Validators.alphanumeric(v)
        else:
            valid = True
            for char in str(value):
                if char.isalnum() or char == ' ':
                    continue
                valid = False
                break
            if valid is False:
                raise ValidationError(
                    'Only alphanumeric characters are allowed.')

    @staticmethod
    def numeric(value):
        """Validate every character in value is numeric."""
        if not value.isdigit():
            raise ValidationError('Not a valid barcode.')

    def limit_characters(characters):
        """Return validator checking every character in value is allowed."""
        def character_limit(value):
            """Check every character in value is allowed for the field."""
            error_message = 'Allowed characters are letters, numbers or {}.'
            if isinstance(value, list):
                for v in value:
                    Validators.character_limit(v)
                    return
            else:
                valid = True
                for char in str(value):
                    if char == ' ' or char.isalnum() or char in characters:
                        continue
                    valid = False
                    break
                if valid is False:
                    raise ValidationError(error_message.format(characters))
        return character_limit

    @classmethod
    def option_value(cls, option_name):
        """Return allowed characters for the given Product Option."""
        allowed_characters = {
            'Size': ['+', '-', '.', '/', "'", '"'],
            'Weight': ['.'],
            'Strength': ['+', '-', '.'],
            'Material': ['%', ','],
        }
        if option_name in allowed_characters:
            return cls.limit_characters(allowed_characters[option_name])
        return cls.alphanumeric


class FormField(forms.Field):
    """Base class for product fields."""

    label = None
    name = None
    field = None
    variable = False
    variation = False
    must_vary = False
    help_text = None
    placeholder = None
    html_class = None
    size = None
    small_size = None
    initial = None
    required_message = ''
    validators = []
    disallowed_characters = []

    def __init__(self, *args, **kwargs):
        """Set field attributes."""
        if self.is_required:
            kwargs['required'] = True
            self.error_messages = {'required': self.required_message}
        else:
            kwargs['required'] = False
        if 'small' in kwargs:
            if kwargs['small'] is True:
                self.size = self.small_size
            kwargs.pop('small')
        kwargs['label'] = self.label
        kwargs['help_text'] = self.help_text
        kwargs['validators'] = self.validators
        if self.initial is not None:
            kwargs['initial'] = self.initial
        if 'html_class' in kwargs:
            self.html_class = kwargs.pop('html_class')
        if isclass(self.widget):
            self.widget = self.get_widget()
        self.kwargs = kwargs
        super().__init__(*args, **kwargs)

    @property
    def is_required(self):
        """Return True if field is required, else False."""
        if len(self.required_message) > 0:
            return True
        return False

    def get_widget(self):
        """Return widget for field."""
        attrs = {}
        if self.placeholder is not None:
            attrs['placeholder'] = self.placeholder
        if self.html_class is not None:
            attrs['class'] = self.html_class
        if self.size is not None:
            attrs['size'] = self.size
        if self.is_required:
            attrs['required'] = 'true'
        return self.widget(attrs=attrs)

    def clean(self, value):
        """Clean submitted value."""
        if value is not None:
            if any((c in value for c in self.disallowed_characters)):
                raise ValidationError(
                    "The following characters are not allowed in "
                    "this field: {}".format(
                        ', '.join(self.disallowed_characters)))
        return super().clean(value)


class ChoiceField(FormField, forms.ChoiceField):
    """Base class for product fields inheriting from ChoiceField."""

    variable = False
    variation = False
    must_vary = False
    size = None
    small_size = None

    def __init__(self, *args, **kwargs):
        """Set field attributes."""
        if 'choices' not in kwargs:
            kwargs['choices'] = self.get_choices()
        kwargs['label'] = self.label
        kwargs = super().__init__(*args, **kwargs)


class BaseSelectizeField(FormField):
    """Base class for choice fields using selectize.js."""

    selectize_options = {}

    def __init__(self, *args, **kwargs):
        """Set field attributes."""
        if 'choices' in kwargs:
            self.choices = kwargs['choices']
        else:
            self.choices = self.get_choices()
            kwargs['choices'] = self.choices
        if 'label' in kwargs:
            self.label = kwargs.pop('label')
        kwargs = super().__init__(*args, **kwargs)

    def get_widget(self):
        """Return widget for field."""
        attrs = {}
        if self.placeholder is not None:
            attrs['placeholder'] = self.placeholder
        if self.html_class is not None:
            attrs['class'] = self.html_class
        if self.size is not None:
            attrs['size'] = self.size
        return self.widget_class(
            attrs=attrs, selectize_options=self.selectize_options,
            choices=self.choices)


class SelectizeField(BaseSelectizeField, forms.MultipleChoiceField):
    """Base class for selectize fields allowing multiple values."""

    widget_class = widgets.MultipleSelectizeWidget

    def to_python(self, *args, **kwargs):
        """Return submited values as a list."""
        value = super().to_python(*args, **kwargs)
        if isinstance(value, str):
            return value.split(',')
        return value


class SingleSelectize(BaseSelectizeField, forms.ChoiceField):
    """Base class for selectize fields allowing a single value."""

    widget_class = widgets.SingleSelectizeWidget
    selectize_options = {'maxItems': 1, "dropdownParent": "body"}

    def to_python(self, *args, **kwargs):
        """Return submitted value as a string."""
        value = super().to_python(*args, **kwargs)
        if isinstance(value, list):
            return value[0]
        return value


class NumberField(FormField, forms.IntegerField):
    """Base class for fields that only accept numeric values."""

    size = None
    small_size = None

    def to_python(self, value):
        """Clean submitted value."""
        value = super().to_python(value)
        if value in self.empty_values:
            return self.empty_value
        return value

    def clean(self, value):
        """If value is blank return zero."""
        value = super().clean(value)
        if not value:
            value = 0
        return value


class PriceField(FormField, forms.FloatField):
    """Base class for product fields for handeling monetary values."""

    size = None
    small_size = None


class CheckboxField(FormField, forms.BooleanField):
    """Base class for product fields using a checkbox widget."""

    pass


class TextField(FormField, forms.CharField):
    """Base class for product fields using a text input."""

    def __init__(self, *args, **kwargs):
        """Instansiate object."""
        FormField.__init__(self, *args, **kwargs)
        forms.CharField.__init__(self, *args, **self.kwargs)

    def clean(self, value):
        """Clean whitespace from submitted value."""
        return super().clean(value).strip()


class TextareaField(FormField, forms.CharField):
    """Base class for product field using the textarea widget."""

    widget = forms.Textarea


class CombinationField(forms.MultiValueField):
    """Base class for product fields inheriting from MultiValueField."""

    help_text = ''

    def __init__(self, *args, **kwargs):
        """Prevent class attributes being lost during instantiation."""
        super().__init__(*args, **kwargs)
        self.help_text = self.__class__.help_text
        self.label = self.__class__.label
