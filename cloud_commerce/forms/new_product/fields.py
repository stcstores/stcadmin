from ccapi import CCAPI

from stcadmin import settings
from . import fieldtypes
from . fieldtypes import Validators


CCAPI.create_session(settings.CC_LOGIN, settings.CC_PWD)


class Title(fieldtypes.TextField):
    label = 'Title'
    name = 'title'
    required_message = "Please supply a range title"
    placeholder = 'Title'
    validators = [Validators.alphanumeric]


class Description(fieldtypes.TextareaField):
    required = False
    label = 'Description'
    name = 'description'
    placeholder = 'Description. Will default to title if left blank'


class Barcode(fieldtypes.TextField):
    label = 'Barcode'
    name = 'barcode'
    required_message = "Please supply a barcode"
    placeholder = 'Barcode'
    must_vary = True


class Department(fieldtypes.ChoiceField):
    label = 'Department'
    name = 'department'
    placeholder = 'Description. Will default to title if left blank'

    @staticmethod
    def get_choices():
        return [
            (dept.value, dept.value) for dept in
            CCAPI.get_option_values("34325")]


class Price(fieldtypes.PriceField):
    label = 'Price (ex VAT)'
    name = 'price'
    required_message = "Please supply a price"
    help_text = 'Price without shipping or VAT'
    variable = True


class PurchasePrice(fieldtypes.PriceField):
    label = 'Purchase Price'
    name = 'purchase_price'
    required_message = 'Please provide a stock level. This can be zero.'
    variable = True
    empty_value = 0.0


class StockLevel(fieldtypes.NumberField):
    label = 'Stock Level'
    name = 'stock_level'
    initial = 0
    required_message = 'Please provide a stock level. This can be zero.'
    variable = True
    empty_value = 0


class VATRate(fieldtypes.ChoiceField):
    label = 'VAT Rate'
    name = 'vat_rate'
    variable = True

    @staticmethod
    def get_choices():
        return ([
            (5, 'Normal Rate 20%'), (2, 'Reduced 5%'), (1, 'VAT Exempt')])


class Supplier(fieldtypes.ChoiceField):
    label = 'Supplier'
    name = 'supplier'

    @staticmethod
    def get_choices():
        suppliers = [
            (supplier.value, supplier.value) for supplier in
            CCAPI.get_option_values("35131")]
        suppliers.sort(key=lambda x: x[1])
        return suppliers


class SupplierSKU(fieldtypes.TextField):
    label = 'Supplier SKU'
    name = 'supplier_SKU'
    placeholder = 'Supplier SKU'
    variable = True


class Weight(fieldtypes.NumberField):
    label = 'Weight (Grams)'
    name = 'weight'
    required_message = "Please supply a weight"
    variable = True
    empty_value = 0


class Height(fieldtypes.NumberField):
    label = 'Height (Milimeters)'
    name = 'height'
    variable = True
    empty_value = 0


class Width(fieldtypes.NumberField):
    label = 'Width (Milimeters)'
    name = 'width'
    variable = True
    empty_value = 0


class Length(fieldtypes.NumberField):
    label = 'Length (Milimeters)'
    name = 'length'
    variable = True
    empty_value = 0


class PackageType(fieldtypes.ChoiceField):
    label = 'Package Type'
    name = 'package_type'
    variable = True

    @staticmethod
    def get_choices():
        return [
            (service.value, service.value)
            for service in CCAPI.get_option_values("33852")]


class Location(fieldtypes.TextField):
    label = 'Location'
    name = 'location'
    placeholder = 'Location'
    variable = True


class Brand(fieldtypes.TextField):
    label = 'Brand'
    name = 'brand'
    required_message = "Please supply a brand"
    placeholder = 'Brand'


class Manufacturer(fieldtypes.TextField):
    label = 'Manufacturer'
    name = 'manufacturer'
    required_message = "Please supply a manufacturer",
    placeholder = 'Manufacturer'


class MetaFormFields(type):

    def __iter__(self):
        for field in self.fields:
            yield field


class DeleteVariation(fieldtypes.CheckboxField):

    label = 'Delete'
    html_class = 'delete_variation'


class FormFields(metaclass=MetaFormFields):
    fields = [
        Title,
        Description,
        Barcode,
        Price,
        PurchasePrice,
        StockLevel,
        VATRate,
        Department,
        Supplier,
        SupplierSKU,
        Weight,
        Height,
        Width,
        Length,
        PackageType,
        Location,
        Brand,
        Manufacturer,
        ]

    delete_variation = DeleteVariation

    variable_fields = [
        field for field in fields if field.variable or field.must_vary]

    option_names = [
        option.option_name for option in CCAPI.get_product_options()
        if option.exclusions['tesco'] is False]

    option_fields = [
        fieldtypes.option_field_factory(option) for option in option_names]

    select_option_fields = [
        fieldtypes.option_selection_field_factory(option) for
        option in option_names]

    option_value_fields = [
        fieldtypes.variation_option_value_field_factory(option) for
        option in option_names]
