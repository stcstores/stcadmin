from django import forms
from django.forms import formset_factory

import itertools

from . fields import FormFields


class NewProductForm(forms.Form):
    field_size = 50


class NewSingleProductForm(NewProductForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in FormFields.fields + FormFields.option_fields:
            self.fields[field.name] = field()


class NewVariationProductForm(NewProductForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_fields()

    def create_fields(self):
        [self.create_field(field) for field in FormFields.fields]
        for field in FormFields.select_option_fields:
            self.fields[field.name] = field()

    def create_field(self, field):
        self.fields[field.name] = field()
        if field.variable:
            self.fields['variable_' + field.name] = forms.BooleanField(
                required=False)
        if field.variation:
            self.fields['variation_' + field.name] = forms.BooleanField(
                required=False)

    def clean(self):
        cleaned_data = super().clean()
        selected_options = []
        variable_options = []
        for key, value in cleaned_data.items():
            if 'opt_' in key:
                if value == 'variation':
                    selected_options.append(self.fields[key].label)
                elif value == 'variable':
                    variable_options.append(self.fields[key].label)
        cleaned_data['selected_options'] = selected_options
        return cleaned_data


class TempVariationForm(NewVariationProductForm):

    def create_fields(self):
        for field in FormFields.select_option_fields:
            self.fields[field.name] = field()


class VariationChoicesForm(forms.Form):

    def set_options(self, options):
        for field in FormFields.option_value_fields:
            if field.label in options:
                self.fields[field.name] = field()

    def clean(self):
        cleaned_data = super().clean()
        variation_values = []
        for key in cleaned_data:
            variation_values.append(
                [(key, value) for value in cleaned_data[key]])
        variations = list(itertools.product(*variation_values))
        variation_data = []
        for variation in variations:
            variation_data.append(
                {option: value for option, value in variation})
        cleaned_data['variations'] = variation_data
        return cleaned_data


class VariationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_variation_fields(self, variations):
        print(variations)
        for field in FormFields.option_fields:
            print(field.label)
            if field.label in variations:
                self.fields[field.name] = field(size=5)


VariationFormSet = formset_factory(VariationForm, extra=0)
