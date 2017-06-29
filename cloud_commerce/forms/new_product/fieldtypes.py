import json
from inspect import isclass

from django import forms
from django.core.exceptions import ValidationError

from . import widgets


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
    size = 50
    initial = None
    required_message = ''

    def __init__(self, *args, **kwargs):
        if self.is_required:
            kwargs['required'] = True
            self.error_messages = {'required': self.required_message}
        else:
            kwargs['required'] = False
        if isclass(self.widget):
            self.widget = self.get_widget()
        kwargs['label'] = self.label
        kwargs['help_text'] = self.help_text
        super().__init__(*args, **kwargs)

    @property
    def is_required(self):
        if len(self.required_message) > 0:
            return True
        return False

    @classmethod
    def get_widget(cls):
        attrs = {}
        if cls.placeholder is not None:
            attrs['placeholder'] = cls.placeholder
        if cls.html_class is not None:
            attrs['class'] = cls.html_class
        if cls.size is not None:
            attrs['size'] = cls.size
        return cls.widget(attrs=attrs)


class ChoiceField(forms.ChoiceField):
    variable = False
    variation = False
    must_vary = False

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = self.get_choices()
        kwargs['label'] = self.label
        super().__init__(*args, **kwargs)


class NumberField(FormField, forms.IntegerField):

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = 0
        super().__init__(*args, **kwargs)


class PriceField(FormField, forms.FloatField):

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = '0.00'
        super().__init__(*args, **kwargs)


class TextField(FormField, forms.CharField):
    pass


class TextareaField(FormField, forms.CharField):
    widget = forms.Textarea


class OptionField(TextField):

    required = False
    variable = True
    variation = True
    must_vary = False
    size = 50

    def __init__(self, *args, **kwargs):
        if 'size' in kwargs:
            self.size = kwargs.pop('size')
        self.widget = forms.TextInput({'size': self.size})
        kwargs['label'] = self.option
        super().__init__(*args, **kwargs)


class OptionSettingField(forms.MultiValueField):

    def __init__(self, *args, **kwargs):
        kwargs['label'] = self.option
        kwargs['initial'] = ('unused', [], '')
        fields = (
            forms.ChoiceField(
                required=True,
                choices=widgets.OptionSettingsFieldWidget.radio_choices),
            ListField(minimum=0, required=False),
            forms.CharField(required=False))
        kwargs['widget'] = widgets.OptionSettingsFieldWidget(None)
        super().__init__(
            fields=fields, require_all_fields=False, *args, **kwargs)

    def clean(self, value):
        clean_data = []
        for i, field in enumerate(self.fields):
            field_value = value[i]
            clean_data.append(field.clean(field_value))
        out = self.compress(clean_data)
        self.validate(out)
        self.run_validators(out)
        return out

    def compress(self, data_list):
        use = data_list[0]
        if use == 'unused':
            return (use, '')
        if use == 'single':
            return (use, data_list[2])
        if use == 'variable':
            return (use, data_list[2])
        if use == 'variation':
            return (use, data_list[1])


class ListField(forms.CharField):

    widget = widgets.ListWidget
    minimum = 0
    maximum = 0
    required = False

    def __init__(self, *args, **kwargs):
        if 'widget' in kwargs:
            self.widget = kwargs.pop('widget')
        if 'minimum' in kwargs:
            self.minimum = kwargs.pop('minimum')
        if 'maximum' in kwargs:
            self.maximum = kwargs.pop('maximum')
        self.required = kwargs['required']
        super().__init__(*args, **kwargs)

    def validate(self, value):
        super().validate(value)
        try:
            json_value = json.loads(value)
        except ValueError:
            raise ValidationError('Not valid JSON.')
        if not isinstance(json_value, list):
            raise ValidationError('Not valid JSON list.')
        if self.minimum > 0 and len(json_value) < self.minimum:
            raise ValidationError(
                'At least {} value(s) required'.format(self.minimum))
        if self.maximum > 0 and len(json_value) > self.maximum:
            raise ValidationError(
                'No more than {} values can be supplied'.format(self.maximum))

    def clean(self, value):
        value = super().clean(value)
        return json.loads(value)


class VariationOptionValueField(ListField):

    initial = ''
    minimum = 2

    def __init__(self, *args, **kwargs):
        kwargs['label'] = self.option
        kwargs['initial'] = ''
        super().__init__(*args, **kwargs)


def option_field_factory(option):
    return type(
        '{}OptionField'.format(option),
        (OptionField, ),
        {'option': option, 'name': 'opt_{}'.format(option), 'label': option})


def option_selection_field_factory(option):
    return type(
        '{}OptionSettingField'.format(option),
        (OptionSettingField, ),
        {'option': option, 'name': 'opt_{}'.format(option), 'label': option})


def variation_option_value_field_factory(option):
    return type(
        '{}VariationOptionValueField'.format(option),
        (VariationOptionValueField, ),
        {'option': option, 'name': 'opt_{}'.format(option), 'label': option})
