import itertools

from django import forms
from django.forms import formset_factory

from . import fields
from .fields import FormFields


class NewProductForm(forms.Form):
    field_size = 50


class NewSingleProductForm(NewProductForm):

    title = fields.Title()
    barcode = fields.Barcode()
    purchase_price = fields.PurchasePrice()
    price = fields.VATPrice()
    stock_level = fields.StockLevel()
    # department = fields.Department()
    # location = fields.Location()
    department = fields.DepartmentBayField()
    supplier = fields.Supplier()
    supplier_sku = fields.SupplierSKU()
    weight = fields.Weight()
    height = fields.Height()
    width = fields.Width()
    length = fields.Length()
    package_type = fields.PackageType()
    brand = fields.Brand()
    manufacturer = fields.Manufacturer()
    description = fields.Description()
    gender = fields.Gender()
    amazon_bullet_points = fields.AmazonBulletPoints()
    amazon_search_terms = fields.AmazonSearchTerms()


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
