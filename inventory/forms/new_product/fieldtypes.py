from inspect import isclass

from django import forms
from django.core.exceptions import ValidationError
from inventory.forms import widgets
from list_input import ListInput


class Validators:

    @staticmethod
    def alphanumeric(value):
        valid = True
        for char in str(value):
            if char.isalnum() or char == ' ':
                continue
            valid = False
            break
        if valid is False:
            raise ValidationError('Only alphanumeric characters are allowed.')

    @staticmethod
    def numeric(value):
        if not value.isdigit():
            raise ValidationError('Not a valid barcode.')

    def limit_characters(characters):
        def character_limit(value):
            valid = True
            for char in str(value):
                if char == ' ' or char.isalnum() or char in characters:
                    continue
                valid = False
                break
            if valid is False:
                raise ValidationError(
                    'Allowed characters are letters, numbers or {}.'.format(
                        characters))
        return character_limit

    @classmethod
    def option_value(cls, option_field):
        characters = {
            'opt_Size': ['+', '-', '.', '/', "'", '"'],
            'opt_Weight': ['.'],
            'opt_Strength': ['+', '-', '.'],
            'opt_Material': ['%', ','],
        }
        if option_field.name in characters:
            return cls.limit_characters(characters[option_field.name])
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
    size = 50
    small_size = 15
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
        kwargs['choices'] = self.get_choices()
        kwargs['label'] = self.label
        kwargs = super().__init__(*args, **kwargs)


class SelectizeField(FormField, forms.MultipleChoiceField):

    selectize_options = {}

    def __init__(self, *args, **kwargs):
        self.choices = self.get_choices()
        kwargs['choices'] = self.choices
        kwargs['label'] = self.label
        kwargs = super().__init__(*args, **kwargs)

    def get_widget(self):
        attrs = {}
        if self.placeholder is not None:
            attrs['placeholder'] = self.placeholder
        if self.html_class is not None:
            attrs['class'] = self.html_class
        if self.size is not None:
            attrs['size'] = self.size
        return widgets.SelectizeWidget(
            attrs=attrs, selectize_options=self.selectize_options,
            choices=self.choices)

    def to_python(self, *args, **kwargs):
        value = super().to_python(*args, **kwargs)
        if isinstance(value, str):
            return value.split(',')
        return value


class SingleSelectize(FormField, forms.ChoiceField):

    selectize_options = {'maxItems': 1}

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = self.get_choices()
        kwargs['label'] = self.label
        kwargs = super().__init__(*args, **kwargs)

    def get_widget(self):
        attrs = {}
        if self.placeholder is not None:
            attrs['placeholder'] = self.placeholder
        if self.html_class is not None:
            attrs['class'] = self.html_class
        if self.size is not None:
            attrs['size'] = self.size
        return widgets.SingleSelectizeWidget(
            attrs=attrs, selectize_options=self.selectize_options)


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
            forms.DecimalField(required=True),
            forms.DecimalField(required=True))
        kwargs['widget'] = widgets.VATPriceWidget()
        super().__init__(
            fields=fields, require_all_fields=True, *args, **kwargs)

    def compress(self, data_list):
        vat_rate, ex_vat_price, with_vat_price = data_list
        return {
            'vat_rate': vat_rate, 'ex_vat': ex_vat_price,
            'with_vat_price': with_vat_price}


class OptionField(TextField):

    required = False
    variable = True
    variation = True
    must_vary = False
    size = 50
    help_text = (
        'This option is only used to add information to the listing and must '
        '<b>only</b> be filled out if it is applicable to the product')

    def __init__(self, *args, **kwargs):
        kwargs['label'] = self.option
        self.validators = [Validators.option_value(self)]
        super().__init__(*args, **kwargs)

    def clean(self, value):
        return str(super().clean(value)).strip()


class OptionSettingField(forms.MultiValueField):
    required = False

    def __init__(self, *args, **kwargs):
        kwargs['label'] = self.option
        kwargs['initial'] = ('unused', [], '')
        fields = (
            forms.ChoiceField(
                required=False,
                choices=widgets.OptionSettingsFieldWidget.radio_choices),
            ListInput(minimum=0, required=False),
            forms.CharField(
                required=False))
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
        multi_value = data_list[1]
        single_value = data_list[2]
        if use == 'unused':
            return (use, '')
        if use == 'single':
            Validators.option_value(self)(single_value)
            return (use, single_value)
        if use == 'variable':
            Validators.option_value(self)(single_value)
            return (use, single_value)
        if use == 'variation':
            for value in multi_value:
                Validators.option_value(self)(value)
            return (use, multi_value)


class VariationOptionValueField(ListInput):

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
