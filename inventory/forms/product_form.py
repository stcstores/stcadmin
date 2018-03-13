from django import forms

from .new_product import fields
from .new_product.fieldtypes import option_field_factory


class ProductForm(forms.Form):

    price = fields.VATPrice()
    locations = fields.Location()
    weight = fields.Weight()
    height = fields.Height()
    length = fields.Length()
    width = fields.Width()
    package_type = fields.PackageType()
    purchase_price = fields.PurchasePrice()
    supplier = fields.Supplier()
    supplier_sku = fields.SupplierSKU()

    ignore_options = [
        'Department', 'Brand', 'Manufacturer', 'WooCategory1', 'WooCategory2',
        'WooCategory3', 'International Shipping', 'Package Type', 'Supplier',
        'Purchase Price', 'Date Created', 'Location', 'Supplier SKU',
        'Amazon Bullets', 'Amazon Search Terms', 'Linn SKU', 'Linn Title']

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product')
        self.product_range = kwargs.pop('product_range')
        option_names = kwargs.pop('option_names')
        self.option_names = [
            o for o in option_names if o not in self.ignore_options]
        super().__init__(*args, **kwargs)
        self.fields['locations'] = fields.Location(
            department=self.product.department)
        for option in self.option_names:
            self.fields['opt_' + option] = option_field_factory(option)()

    def save(self, *args, **kwargs):
        product = self.product
        cleaned_data = self.cleaned_data
        product.vat_rate = cleaned_data['vat_rate']
        product.price = cleaned_data['price']
        product.bays = cleaned_data['locations']
        product.weight = cleaned_data['weight']
        product.height = cleaned_data['height']
        product.length = cleaned_data['length']
        product.width = cleaned_data['width']
        product.package_type = cleaned_data['package_type']
        product.purchase_price = cleaned_data['purchase_price']
        product.supplier = cleaned_data['supplier']
        product.supplier_sku = cleaned_data['supplier_sku']
        options = [key[4:] for key in cleaned_data.keys() if key[4:] == 'opt_']
        for option in options:
            value = cleaned_data[option]
            product.options[option] = value
