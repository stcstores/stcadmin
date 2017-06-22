from django import forms
from django.forms import formset_factory

import json

from . fields import FormFields
from . import widgets


class NewProductForm(forms.Form):
    field_size = 50


class NewSingleProductForm(NewProductForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in FormFields:
            self.fields[field.name] = field.field()


class NewVariationProductForm(NewProductForm):
    """
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
        ]"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_fields()

    def create_fields(self):
        [self.create_field(field) for field in FormFields
            if field.option is False]
        [self.create_field(field) for field in FormFields
            if field.option is True]

    def create_option_field(self, field):
        choices = [
            ('{}_unused'.format(field.name), 'Unused'.format(field.name)),
            ('{}_variable'.format(field.name), 'Variable'.format(field.name)),
            ('{}_variation'.format(field.name), 'Variation'.format(field.name))
        ]
        self.fields['opt_' + field.name] = forms.ChoiceField(
            label=field.label, choices=choices, widget=forms.RadioSelect,
            initial='{}_unused'.format(field.name))

    def create_field(self, field):
        self.fields[field.name] = field.field
        if field.variable:
            self.fields['variable_' + field.name] = forms.BooleanField(
                required=False)
        if field.variation:
            self.fields['variation_' + field.name] = forms.BooleanField(
                required=False)


class TempVariationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in FormFields:
            if field.option:
                self.fields['opt_' + field.name] = field.select_field()

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


class VariationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_variation_fields(self, variations):
        for variation in variations:
            self.fields[variation] = forms.CharField()


VariationFormSet = formset_factory(VariationForm, extra=0)
