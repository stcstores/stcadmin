from django import forms

from inventory import models

from .new_product import fields
from .new_product.fieldtypes import option_field_factory


class ProductForm(forms.Form):

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
        self.fields['price'] = fields.VATPrice()
        self.fields['locations'] = fields.DepartmentBayField(
            lock_department=True)
        self.fields['weight'] = fields.Weight()
        self.fields['height'] = fields.Height()
        self.fields['length'] = fields.Length()
        self.fields['width'] = fields.Width()
        self.fields['package_type'] = fields.PackageType()
        self.fields['purchase_price'] = fields.PurchasePrice()
        self.fields['supplier'] = fields.Supplier()
        self.fields['supplier_sku'] = fields.SupplierSKU()
        for option in self.option_names:
            self.fields['opt_' + option] = option_field_factory(option)()
        self.initial = self.get_initial()

    def get_initial(self):
        initial = {}
        department = models.Warehouse.used_warehouses.get(
            name=self.product.department).id
        initial['price'] = (self.product.vat_rate, self.product.price, '')
        initial['locations'] = {
            'department': department, 'bays': self.product.bays}
        initial['weight'] = self.product.weight
        initial['height'] = self.product.height
        initial['length'] = self.product.length
        initial['width'] = self.product.width
        initial['purchase_price'] = self.product.purchase_price
        initial['package_type'] = self.product.package_type
        initial['supplier'] = self.product.supplier.factory_name
        initial['supplier_sku'] = self.product.supplier_sku
        for option in self.option_names:
            initial['opt_' + option] = self.product.options[option]
        return initial

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        self.product.vat_rate = data['price']['vat_rate']
        self.product.price = data['price']['ex_vat']
        self.product.bays = data['locations']['bay']
        self.product.weight = data['weight']
        self.product.height = data['height']
        self.product.length = data['length']
        self.product.width = data['width']
        self.product.package_type = data['package_type']
        self.product.purchase_price = data['purchase_price']
        self.product.supplier = data['supplier']
        self.product.supplier_sku = data['supplier_sku']
        options = [key[4:] for key in data.keys() if key[4:] == 'opt_']
        for option in options:
            value = data[option]
            self.product.options[option] = value
