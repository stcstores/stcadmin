from django import forms
from .new_product.fields import Title, Description

from .new_product. fieldtypes import option_field_factory
from .new_product import fields


class ProductRangeForm(forms.Form):
    end_of_line = forms.BooleanField(required=False)


class DescriptionForm(forms.Form):
    title = Title()
    description = Description()
    amazon_bullets = fields.AmazonBulletPoints()
    search_terms = fields.AmazonSearchTerms()


class ProductForm(forms.Form):

    vat_rate = fields.VATRate()
    price = fields.Price()
    weight = fields.Weight()
    height = fields.Height()
    length = fields.Length()
    width = fields.Width()
    package_type = fields.PackageType()
    purchase_price = fields.PurchasePrice()
    supplier_sku = fields.SupplierSKU()

    ignore_options = [
        'Department', 'Brand', 'Manufacturer', 'WooCategory1', 'WooCategory2',
        'WooCategory3', 'International Shipping', 'Package Type', 'Supplier',
        'Purchase Price', 'Date Created', 'Location', 'Supplier SKU',
        'Amazon Bullets', 'Amazon Search Terms']

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product')
        self.product_range = kwargs.pop('product_range')
        option_names = kwargs.pop('option_names')
        self.option_names = [
            o for o in option_names if o not in self.ignore_options]
        super().__init__(*args, **kwargs)
        for option in self.option_names:
            self.fields['opt_' + option] = option_field_factory(option)()
