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
        for field in FormFields.fields:
            if not field.must_vary:
                self.create_field(field)
        for field in FormFields.select_option_fields:
            self.fields[field.name] = field()

    def create_field(self, field):
        self.fields[field.name] = field()
        if field.variable is True and field.must_vary is False:
            self.fields['variable_' + field.name] = forms.BooleanField(
                required=False)
        if field.variation:
            self.fields['variation_' + field.name] = forms.BooleanField(
                required=False)

    def clean(self):
        cleaned_data = super().clean()
        selected_options = []
        variable_options = []
        for field in FormFields.fields:
            if field.variable and cleaned_data['variable_' + field.name]:
                variable_options.append(field.name)
        for key, value in cleaned_data.items():
            if 'opt_' in key:
                if value == 'variation':
                    selected_options.append(self.fields[key].name)
                elif value == 'variable':
                    variable_options.append(self.fields[key].name)
        cleaned_data['selected_options'] = selected_options
        cleaned_data['selected_variables'] = variable_options
        return cleaned_data


class TempVariationForm(NewVariationProductForm):

    def create_fields(self):
        for field in FormFields.select_option_fields:
            self.fields[field.name] = field()


class VariationChoicesForm(forms.Form):

    def set_options(self, options):
        for field in FormFields.option_value_fields:
            if field.name in options:
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

    def set_variation_fields(self, variations, variables):
        for field in FormFields.option_fields:
            if field.name in variations:
                self.fields[field.name] = field(size=15)
        for field in FormFields.variable_fields:
            if field.name in variables or field.must_vary:
                self.fields[field.name] = field()
        for field in FormFields.option_fields:
            if field.name in variables:
                self.fields[field.name] = field(size=15)


VariationFormSet = formset_factory(VariationForm, extra=0)
