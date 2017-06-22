from inspect import isclass
import json

from django import forms
from django.core.exceptions import ValidationError

from stcadmin import settings
from . import widgets

from ccapi import CCAPI


CCAPI.create_session(settings.CC_LOGIN, settings.CC_PWD)


class MetaFormFields(type):

    def __iter__(self):
        for field in self.fields:
            yield field


class FormField(forms.Field):

    label = None
    name = None
    field = None
    variable = False
    variation = False
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
    size = 50

    def __init__(self, *args, **kwargs):
        if 'size' in kwargs:
            self.size = kwargs.pop('size')
        self.widget = forms.TextInput({'size': self.size})
        kwargs['label'] = self.option
        super().__init__(*args, **kwargs)


class OptionSelectionField(forms.ChoiceField):

    widget = forms.RadioSelect

    def __init__(self, *args, **kwargs):
        kwargs['label'] = self.option
        kwargs['choices'] = self.get_choices()
        kwargs['initial'] = kwargs['choices'][0][0]
        super().__init__(*args, **kwargs)

    def get_choices(self):
        return [
            ('unused'.format(self.name), 'Unused'),
            ('variable'.format(self.name), 'Variable'),
            ('variation'.format(self.name), 'Variation')]


class ListField(forms.CharField):

    widget = widgets.ListWidget
    minimum = 0
    maximum = 0
    required = False

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


class Title(TextField):
    label = 'Title'
    name = 'title'
    required_message = "Please supply a range title"
    placeholder = 'Title'


class Description(TextareaField):
    required = False
    label = 'Description'
    name = 'description'
    placeholder = 'Description. Will default to title if left blank'


class Barcode(TextField):
    label = 'Barcode'
    name = 'barcode'
    required_message = "Please supply a barcode"
    placeholder = 'Barcode'
    variable = True


class Department(ChoiceField):
    label = 'Department'
    name = 'department'
    placeholder = 'Description. Will default to title if left blank'

    @staticmethod
    def get_choices():
        return [
            (dept.value, dept.value) for dept in
            CCAPI.get_option_values("34325")]


class Price(PriceField):
    label = 'Price (ex VAT)'
    name = 'price'
    required_message = "Please supply a price"
    help_text = 'Price without shipping or VAT'
    variable = True


class PurchasePrice(PriceField):
    label = 'Purchase Price'
    name = 'purchase_price'
    initial = 0,
    required_message = 'Please provide a stock level. This can be zero.'
    variable = True


class StockLevel(NumberField):
    label = 'Stock Level'
    name = 'stock_level'
    initial = 0
    required_message = 'Please provide a stock level. This can be zero.'
    variable = True


class VATRate(ChoiceField):
    label = 'VAT Rate'
    name = 'vat_rate'
    variable = True

    @staticmethod
    def get_choices():
        return ([
            (5, 'Normal Rate 20%'), (2, 'Reduced 5%'), (1, 'VAT Exempt')])


class Supplier(ChoiceField):
    label = 'Supplier'
    name = 'supplier'

    @staticmethod
    def get_choices():
        suppliers = [
            (supplier.value, supplier.value) for supplier in
            CCAPI.get_option_values("35131")]
        suppliers.sort(key=lambda x: x[1])
        return suppliers


class SupplierSKU(TextField):
    label = 'Supplier SKU'
    name = 'supplier_SKU'
    placeholder = 'Supplier SKU'
    variable = True


class Weight(NumberField):
    label = 'Weight (Grams)'
    name = 'weight'
    required_message = "Please supply a weight"
    variable = True


class Height(NumberField):
    label = 'Height (Milimeters)'
    name = 'height'
    variable = True


class Width(NumberField):
    label = 'Width (Milimeters)'
    name = 'width'
    variable = True


class Length(NumberField):
    label = 'Length (Milimeters)'
    name = 'length'
    variable = True


class PackageType(ChoiceField):
    label = 'Package Type'
    name = 'package_type'
    variable = True

    @staticmethod
    def get_choices():
        return [
            (service.value, service.value)
            for service in CCAPI.get_option_values("33852")]


class Location(TextField):
    label = 'Location'
    name = 'location'
    placeholder = 'Location'
    variable = True


class Brand(TextField):
    label = 'Brand'
    name = 'brand'
    required_message = "Please supply a brand"
    placeholder = 'Brand'


class Manufacturer(TextField):
    label = 'Manufacturer'
    name = 'manufacturer'
    required_message = "Please supply a manufacturer",
    placeholder = 'Manufacturer'


def option_field_factory(option):
    return type('{}OptionField'.format(option), (OptionField, ), {
        'option': option, 'name': 'opt_{}'.format(option), 'label': option})


def option_selection_field_factory(option):
    return type('{}SelectionField'.format(option), (OptionSelectionField, ), {
        'option': option, 'name': 'opt_{}'.format(option), 'label': option})


def variation_option_value_field_factory(option):
    return type(
        '{}VariationOptionValueField'.format(option),
        (VariationOptionValueField, ),
        {'option': option, 'name': 'opt_{}'.format(option), 'label': option})


class FormFields(metaclass=MetaFormFields):
    fields = [
        Title,
        Description,
        Barcode,
        Department,
        Price,
        PurchasePrice,
        StockLevel,
        VATRate,
        Supplier,
        SupplierSKU,
        Weight,
        Height,
        Width,
        Length,
        PackageType,
        Location,
        Brand,
        Manufacturer,
        ]

    option_names = [
        option.option_name for option in CCAPI.get_product_options()
        if option.exclusions['tesco'] is False]

    option_fields = [option_field_factory(option) for option in option_names]

    select_option_fields = [
        option_selection_field_factory(option) for option in option_names]

    option_value_fields = [
        variation_option_value_field_factory(option) for
        option in option_names]
