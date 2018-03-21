from ccapi import CCAPI
from django import forms
from stcadmin.forms import KwargFormSet

from . import fields, fieldtypes


class NewProductForm(forms.Form):
    field_size = 50


class NewProductBasicForm(NewProductForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'] = fields.Title()
        self.fields['barcode'] = fields.Barcode()
        self.fields['purchase_price'] = fields.PurchasePrice()
        self.fields['price'] = fields.VATPrice()
        self.fields['stock_level'] = fields.StockLevel()
        self.fields['department'] = fields.DepartmentBayField()
        self.fields['supplier'] = fields.Supplier()
        self.fields['supplier_sku'] = fields.SupplierSKU()
        self.fields['weight'] = fields.Weight()
        self.fields['height'] = fields.Height()
        self.fields['width'] = fields.Width()
        self.fields['length'] = fields.Length()
        self.fields['package_type'] = fields.PackageType()
        self.fields['brand'] = fields.Brand()
        self.fields['manufacturer'] = fields.Manufacturer()
        self.fields['description'] = fields.Description()
        self.fields['gender'] = fields.Gender()
        self.fields['amazon_bullet_points'] = fields.AmazonBulletPoints()
        self.fields['amazon_search_terms'] = fields.AmazonSearchTerms()


class VariationOptionsForm(NewProductForm):

    def __init__(self, *args, **kwargs):
        self.option_data = kwargs.pop(
            'option_data', CCAPI.get_product_options())
        self.options = self.get_options()
        super().__init__(*args, **kwargs)
        self.get_fields()

    def get_fields(self):
        for option_name, values in self.options:
            choices = [
                (v, v) for v in self.get_choice_values(option_name, values)]
            self.fields[option_name] = fields.SelectOptions(
                option_name, choices)

    def get_choice_values(self, option_name, values):
        if option_name in self.initial:
            new_values = [
                v for v in self.initial[option_name] if v not in values]
            values += new_values
        return values

    def get_options(self):
        return [
            (option.option_name, [value.value for value in option]) for option
            in self.option_data if option.exclusions['tesco'] is False]


class VariationForm(NewProductForm):

    def __init__(self, *args, **kwargs):
        self.variation_options = kwargs.pop('variation_options')
        choices = kwargs.pop('choices')
        supplier_choices = choices['supplier']
        package_type_choices = choices['package_type']
        self.option_values = kwargs.pop('option_values')
        super().__init__(*args, **kwargs)
        self.fields['barcode'] = fields.Barcode()
        self.fields['purchase_price'] = fields.PurchasePrice()
        self.fields['price'] = fields.VATPrice()
        self.fields['stock_level'] = fields.StockLevel()
        self.fields['department'] = fields.DepartmentBayField()
        self.fields['supplier'] = fields.Supplier(choices=supplier_choices)
        self.fields['supplier_sku'] = fields.SupplierSKU()
        self.fields['weight'] = fields.Weight()
        self.fields['height'] = fields.Height()
        self.fields['width'] = fields.Width()
        self.fields['length'] = fields.Length()
        self.fields['package_type'] = fields.PackageType(
            choices=package_type_choices)
        self.fields['brand'] = fields.Brand()
        self.fields['manufacturer'] = fields.Manufacturer()
        self.fields['gender'] = fields.Gender()
        self.get_fields()
        self.order_fields(list(self.variation_options.keys()))

    def get_fields(self):
        for option_name, value in self.variation_options.items():
            self.fields[option_name] = forms.CharField(
                max_length=255, initial=value, widget=forms.HiddenInput())
        for option_name, values in self.option_values.items():
            if option_name not in self.variation_options:
                choices = [('', '')] + [(v, v) for v in self.get_choice_values(
                    option_name, values)]
                self.fields[option_name] = fieldtypes.SingleSelectize(
                    choices=choices)

    def get_choice_values(self, option_name, values):
        if option_name in self.initial:
            if self.initial[option_name] not in values:
                values.append(self.initial[option_name])
        return values


class VariationFormSet(KwargFormSet):
    form = VariationForm

    def __init__(self, *args, **kwargs):
        option_data = CCAPI.get_product_options()
        option_values = {
            option.option_name: [value.value for value in option] for option
            in option_data if option.exclusions['tesco'] is False}
        choices = {
            'supplier': fields.Supplier.get_choices(),
            'package_type': fields.PackageType.get_choices()}
        for form_kwargs in kwargs['form_kwargs']:
            form_kwargs['choices'] = choices
            form_kwargs['option_values'] = option_values
        super().__init__(*args, **kwargs)


"""

class NewVariationProductForm(NewProductForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_fields()

    def create_fields(self):
        for field in FormFields.fields:
            if not field.must_vary:
                self.create_field(field)
        for field in FormFields.select_option_fields:
            self.create_option_field(field)

    def create_field(self, field):
        self.fields[field.name] = field()
        if field.variable is True and field.must_vary is False:
            self.fields['variable_' + field.name] = forms.BooleanField(
                required=False)
        if field.variation:
            self.fields['variation_' + field.name] = forms.BooleanField(
                required=False)

    def create_option_field(self, field):
        self.fields[field.name] = field()

    def clean(self):
        cleaned_data = super().clean()
        if self.is_valid():
            selected_options = []
            variable_options = {}
            variation_values = []
            for field in FormFields.fields:
                if field.variable and cleaned_data['variable_' + field.name]:
                    variable_options[field.name] = cleaned_data[field.name]
            for field in FormFields.option_fields:
                use = cleaned_data[field.name][0]
                value = cleaned_data[field.name][1]
                if use == 'variation':
                    selected_options.append(field.name)
                    variation_values.append(
                        [(field.name, variation) for variation in value])
                elif use == 'variable':
                    variable_options[field.name] = value
            cleaned_data['selected_options'] = selected_options
            cleaned_data['selected_variables'] = variable_options
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
        self.variation_fields = [
            field for field in FormFields.option_fields if field.name in
            variations]
        self.variable_fields = [
            field for field in FormFields.variable_fields if field.name in
            variables or field.must_vary]
        self.variable_option_fields = [
            field for field in FormFields.option_fields if field.name in
            variables]
        for field in self.variation_fields:
            self.fields[field.name] = field(
                small=True, disabled=True, html_class='variation_option')
        for field in self.variable_fields:
            self.fields[field.name] = field(small=True)
        for field in self.variable_option_fields:
            self.fields[field.name] = field(
                small=True, html_class='variable_option')


VariationFormSet = formset_factory(VariationForm, extra=0, can_delete=True)
"""
