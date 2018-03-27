from ccapi import CCAPI
from django import forms

from stcadmin.forms import KwargFormSet

from . import fields, fieldtypes


class NewProductForm(forms.Form):
    field_size = 50


class BasicInfo(NewProductForm):

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


class BaseOptionsForm(NewProductForm):

    def __init__(self, *args, **kwargs):
        self.option_data = kwargs.pop(
            'option_data', CCAPI.get_product_options())
        self.options = self.get_options()
        super().__init__(*args, **kwargs)
        self.get_fields()

    def get_options(self):
        return [
            (option.option_name, [value.value for value in option]) for option
            in self.option_data if option.exclusions['tesco'] is False]

    def get_choice_values(self, option_name, values):
        if option_name in self.initial:
            new_values = [
                v for v in self.initial[option_name] if v not in values]
            values += new_values
        return values

    def get_fields(self):
        for option_name, values in self.options:
            choices = [('', '')] + [
                (v, v) for v in self.get_choice_values(option_name, values)]
            self.fields[option_name] = self.field_class(
                label=option_name, choices=choices)


class VariationOptions(BaseOptionsForm):
    field_class = fields.SelectOptions


class ListingOptions(BaseOptionsForm):
    field_class = fieldtypes.SingleSelectize


class BaseVariationForm(NewProductForm):

    def __init__(self, *args, **kwargs):
        self.variation_options = kwargs.pop('variation_options')
        self.existing_data = kwargs.pop('existing_data')
        super().__init__(*args, **kwargs)
        self.get_fields()
        self.update_initial()
        self.order_fields(list(self.variation_options.keys()))

    def update_initial(self):
        if self.existing_data is not None:
            for variation in self.existing_data:
                correct_form = all([
                    variation.get(key) == self.variation_options.get(key)
                    for key in self.variation_options])
                if correct_form:
                    self.initial.update(variation)

    def get_choice_values(self, option_name, values):
        if option_name in self.initial:
            if self.initial[option_name] not in values:
                values.append(self.initial[option_name])
        return values


class VariationInfo(BaseVariationForm):

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices')
        self.supplier_choices = choices['supplier']
        self.package_type_choices = choices['package_type']
        super().__init__(*args, **kwargs)

    def get_fields(self):
        self.fields['barcode'] = fields.Barcode()
        self.fields['purchase_price'] = fields.PurchasePrice()
        self.fields['price'] = fields.VATPrice()
        self.fields['stock_level'] = fields.StockLevel()
        self.fields['department'] = fields.DepartmentBayField()
        self.fields['supplier'] = fields.Supplier(
            choices=self.supplier_choices)
        self.fields['supplier_sku'] = fields.SupplierSKU()
        self.fields['weight'] = fields.Weight()
        self.fields['height'] = fields.Height()
        self.fields['width'] = fields.Width()
        self.fields['length'] = fields.Length()
        self.fields['package_type'] = fields.PackageType(
            choices=self.package_type_choices)
        self.fields['brand'] = fields.Brand()
        self.fields['manufacturer'] = fields.Manufacturer()
        self.fields['gender'] = fields.Gender()
        for option_name, value in self.variation_options.items():
            self.fields[option_name] = forms.CharField(
                max_length=255, initial=value, widget=forms.HiddenInput())


class VariationListingOptions(BaseVariationForm):

    def __init__(self, *args, **kwargs):
        self.option_values = kwargs.pop('option_values')
        super().__init__(*args, **kwargs)

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


class BaseVariationFormSet(KwargFormSet):

    def __init__(self, *args, **kwargs):
        kwarg_update = self.update_form_kwargs()
        for form_kwargs in kwargs['form_kwargs']:
            form_kwargs.update(kwarg_update)
        super().__init__(*args, **kwargs)

    def update_form_kwargs(self):
        raise NotImplementedError()


class VariationInfoSet(BaseVariationFormSet):
    form = VariationInfo

    def update_form_kwargs(self):
        choices = {
            'supplier': fields.Supplier.get_choices(),
            'package_type': fields.PackageType.get_choices()}
        return {'choices': choices}


class VariationListingOptionsSet(BaseVariationFormSet):
    form = VariationListingOptions

    def update_form_kwargs(self):
        option_data = CCAPI.get_product_options()
        option_values = {
            option.option_name: [value.value for value in option] for option
            in option_data if option.exclusions['tesco'] is False}
        return {'option_values': option_values}
