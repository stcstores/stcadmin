from django import forms
from django.forms import formset_factory

import json

from . import fields
from . import widgets


class NewProductForm(forms.Form):
    field_size = 50


class NewSingleProductForm(NewProductForm):

    title = fields.title
    description = fields.description
    barcode = fields.barcode
    department = fields.department
    price = fields.price
    purchase_price = fields.purchase_price
    package_type = fields.package_type
    vat_rate = fields.vat_rate
    stock_level = fields.stock_level
    brand = fields.brand
    manufacturer = fields.manufacturer
    supplier = fields.supplier
    supplier_SKU = fields.supplier_SKU
    weight = fields.weight
    length = fields.length
    height = fields.height
    width = fields.width
    location = fields.location

    def __init__(self, *args, **kwargs):
        super(NewSingleProductForm, self).__init__(*args, **kwargs)
        for option, field in fields.option_fields:
            self.fields['opt_{}'.format(option)] = field


class NewVariationProductForm(NewProductForm):

    setup_fields = [
        fields.VariationField('title', fields.title),
        fields.VariationField('description', fields.description),
        fields.VariationField('barcode', fields.barcode, variable=True),
        fields.VariationField('department', fields.department),
        fields.VariationField('price', fields.price, variable=True),
        fields.VariationField(
            'purchase_price', fields.purchase_price, variable=True),
        fields.VariationField(
            'package_type', fields.package_type, variable=True),
        fields.VariationField('vat_rate', fields.vat_rate, variable=True),
        fields.VariationField(
            'stock_level', fields.stock_level, variable=True),
        fields.VariationField('brand', fields.brand),
        fields.VariationField('manufacturer', fields.manufacturer),
        fields.VariationField('supplier', fields.supplier),
        fields.VariationField(
            'supplier_SKU', fields.supplier_SKU, variable=True),
        fields.VariationField('weight', fields.weight, variable=True),
        fields.VariationField('length', fields.length, variable=True),
        fields.VariationField('height', fields.height, variable=True),
        fields.VariationField('width', fields.width, variable=True),
        fields.VariationField('location', fields.location, variable=True),
        ]

    def __init__(self, *args, **kwargs):
        super(NewVariationProductForm, self).__init__(*args, **kwargs)
        self.create_fields()

    def create_fields(self):
        [self.create_field(field) for field in self.setup_fields]
        for option, field in fields.option_fields:
            choices = [
                ('{}_unused'.format(option), 'Unused'.format(option)),
                ('{}_variable'.format(option), 'Variable'.format(option)),
                ('{}_variation'.format(option), 'Variation'.format(option))]
            self.fields['opt_' + option] = forms.ChoiceField(
                label=option, choices=choices, widget=forms.RadioSelect,
                initial='{}_unused'.format(option))
        self.options = [option for option, field in fields.option_fields]

    def create_field(self, field):
        self.fields[field.title] = field.field
        if field.variable:
            self.fields['variable_' + field.title] = forms.BooleanField(
                required=False)
        if field.variation:
            self.fields['variation_' + field.title] = forms.BooleanField(
                required=False)


class VariationChoicesForm(forms.Form):

    def set_options(self, options):
        for field in self.fields:
            if field not in options:
                self.fields.pop(field)
        for option in options:
            if option not in self.fields:
                self.fields[option] = forms.CharField(
                    required=False, initial=self.data.get(option, ''),
                    widget=widgets.ListWidget())

    def clean(self):
        cleaned_data = super().clean()
        for key, value in cleaned_data.items():
            if len(value) > 0:
                cleaned_data[key] = json.loads(value)
            else:
                cleaned_data[key] = []
        return cleaned_data


class TempVariationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for option, field in fields.option_fields:
            choices = [
                ('{}_unused'.format(option), 'Unused'.format(option)),
                ('{}_variable'.format(option), 'Variable'.format(option)),
                ('{}_variation'.format(option), 'Variation'.format(option))]
            self.fields['opt_' + option] = forms.ChoiceField(
                label=option, choices=choices, widget=forms.RadioSelect,
                initial='{}_unused'.format(option))

    def clean(self):
        cleaned_data = super().clean()
        selected_options = []
        variable_options = []
        for key, value in cleaned_data.items():
            if 'opt_' in key:
                if 'variation' in value:
                    selected_options.append(self.fields[key].label)
                elif 'variable' in value:
                    variable_options.append(self.fields[key])
        cleaned_data['selected_options'] = selected_options
        return cleaned_data


class VariationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_variation_fields(self, variations):
        for variation in variations:
            self.fields[variation] = forms.CharField()


VariationFormSet = formset_factory(VariationForm, extra=0)
