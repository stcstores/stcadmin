from inspect import isclass

from django import forms
from django.core.exceptions import ValidationError

from inventory.forms import widgets


class Validators:

    @staticmethod
    def alphanumeric(value):
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
        if not value.isdigit():
            raise ValidationError('Not a valid barcode.')

    def limit_characters(characters):
        def character_limit(value):
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
        if len(self.required_message) > 0:
            return True
        return False

    def get_widget(self):
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
        if value is not None:
            if any((c in value for c in self.disallowed_characters)):
                raise ValidationError(
                    "The following characters are not allowed in "
                    "this field: {}".format(
                        ', '.join(self.disallowed_characters)))
        return super().clean(value)


class ChoiceField(FormField, forms.ChoiceField):
    variable = False
    variation = False
    must_vary = False
    size = None
    small_size = None

    def __init__(self, *args, **kwargs):
        if 'choices' not in kwargs:
            kwargs['choices'] = self.get_choices()
        kwargs['label'] = self.label
        kwargs = super().__init__(*args, **kwargs)


class BaseSelectizeField(FormField):

    selectize_options = {}

    def __init__(self, *args, **kwargs):
        if 'choices' in kwargs:
            self.choices = kwargs['choices']
        else:
            self.choices = self.get_choices()
            kwargs['choices'] = self.choices
        if 'label' in kwargs:
            self.label = kwargs.pop('label')
        kwargs = super().__init__(*args, **kwargs)

    def get_widget(self):
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
    widget_class = widgets.MultipleSelectizeWidget

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        if isinstance(value, str):
            return value.split(',')
        return value


class SingleSelectize(BaseSelectizeField, forms.ChoiceField):
    widget_class = widgets.SingleSelectizeWidget
    selectize_options = {'maxItems': 1, "dropdownParent": "body"}

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        if isinstance(value, list):
            return value[0]
        return value


class NumberField(FormField, forms.IntegerField):

    size = None
    small_size = None

    def to_python(self, value):
        value = super().to_python(value)
        if value in self.empty_values:
            return self.empty_value
        return value


class PriceField(FormField, forms.FloatField):

    size = None
    small_size = None


class CheckboxField(FormField, forms.BooleanField):
    pass


class TextField(FormField, forms.CharField):

    def __init__(self, *args, **kwargs):
        FormField.__init__(self, *args, **kwargs)
        forms.CharField.__init__(self, *args, **self.kwargs)

    def clean(self, value):
        return super().clean(value).strip()


class TextareaField(FormField, forms.CharField):
    widget = forms.Textarea


class VATPriceField(forms.MultiValueField):
    required = True

    def __init__(self, *args, **kwargs):
        kwargs['label'] = 'Price'
        fields = (
            forms.ChoiceField(
                required=True,
                choices=widgets.VATPriceWidget.vat_choices()),
            forms.FloatField(required=True),
            forms.FloatField(required=True))
        kwargs['widget'] = widgets.VATPriceWidget()
        super().__init__(
            fields=fields, require_all_fields=True, *args, **kwargs)

    def compress(self, data_list):
        vat_rate, ex_vat_price, with_vat_price = data_list
        return {
            'vat_rate': vat_rate, 'ex_vat': ex_vat_price,
            'with_vat_price': with_vat_price}
