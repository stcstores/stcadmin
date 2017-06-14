from django import forms
from . import fields


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
    pass
