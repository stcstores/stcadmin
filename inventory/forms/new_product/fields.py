import json
import re

from ccapi import CCAPI

from inventory import models
from list_input import ListInput

from . import fieldtypes
from .fieldtypes import Validators


class Title(fieldtypes.TextField):
    label = 'Title'
    name = 'title'
    required_message = "Please supply a range title"
    placeholder = 'Title'
    validators = [Validators.limit_characters('%')]
    help_text = 'The title for the <b>Product</b>.'


class Description(fieldtypes.TextareaField):
    required = False
    label = 'Description'
    name = 'description'
    html_class = 'froala'
    placeholder = 'Description. Will default to title if left blank'
    disallowed_characters = ['~']
    help_text = (
        'The Description for the listings.<br>'
        'This can be changed on a channel by channel basis if necessary<br>'
        'If left blank the description will duplicate the title.')

    def clean(self, value):
        value = super().clean(value)
        value = value.replace('&nbsp;', ' ')  # Remove Non breaking spaces
        value = re.sub(' +', ' ', value)  # Remove multiple space characters
        return value


class Barcode(fieldtypes.TextField):
    label = 'Barcode'
    name = 'barcode'
    placeholder = 'Barcode'
    validators = [Validators.numeric]
    must_vary = True
    help_text = (
        "A unique barcode for the product.<br>"
        "If left blank one will be provided from stock.")


class Department(fieldtypes.ChoiceField):
    label = 'Department'
    name = 'department'
    required_message = "A <b>Department</b> must be selected."
    help_text = (
        'The <b>Department</b> to which the product belongs and the '
        '<b>Warehouse</b> to which it will be added.')

    @staticmethod
    def get_choices():
        departments = [
            (dept.value, dept.value) for dept in
            CCAPI.get_option_values("34325")]
        departments.sort(key=lambda x: x[1])
        return [('', '')] + departments


class Price(fieldtypes.PriceField):
    label = 'Price'
    name = 'price'
    required_message = (
        'Please provide a <b>Price</b>. This cannot be blank but can be zero.')
    help_text = (
        'Price <b>without shipping</b>.'
        '<br>Ex VAT cannot be blank but can be zero.')
    variable = True


class PurchasePrice(fieldtypes.PriceField):
    label = 'Purchase Price'
    name = 'purchase_price'
    required_message = (
        'Please provide a <b>Stock Level</b>. '
        'This cannot be blank but can be zero.')
    variable = True
    empty_value = 0.0
    help_text = (
        'Price at which we purchase the product.'
        '<br>Cannot be blank but can be zero.')


class StockLevel(fieldtypes.NumberField):
    label = 'Stock Level'
    name = 'stock_level'
    initial = 0
    required_message = (
        'Please provide a stock level. This cannot be blank but can be zero.')
    variable = True
    empty_value = 0
    help_text = (
        'Initial <b>Stock Level</b> of the product.'
        '<br>Cannot be blank but can be zero.')


class VATRate(fieldtypes.ChoiceField):
    label = 'VAT Rate'
    name = 'vat_rate'
    variable = True
    help_text = 'The VAT rate that is applicable to the product.'
    required_message = (
        'Please specify the appropriate <b>VAT Rate</b> for the '
        'product.')

    @staticmethod
    def get_choices():
        return ([
            ('', ''), (20, 'Normal Rate 20%'), (5, 'Reduced 5%'),
            (0, 'VAT Exempt')])


class Supplier(fieldtypes.ChoiceField):
    label = 'Supplier'
    name = 'supplier'
    required_message = (
        'A <b>Supplier</b> must be provided. If the supplier does appear in '
        'the list it must be added to Cloud Commerce before the product can be'
        ' created.')
    help_text = (
        'The <b>Supplier</b> from which the product is purchased.'
        'If the supplier does appear in the list it must be added to '
        'Cloud Commerce before the product can be created.')

    @staticmethod
    def get_choices():
        suppliers = [
            (supplier.value, supplier.value) for supplier in
            CCAPI.get_option_values("35131")]
        suppliers.sort(key=lambda x: x[1])
        return [('', '')] + suppliers


class SupplierSKU(fieldtypes.TextField):
    label = 'Supplier SKU'
    name = 'supplier_SKU'
    placeholder = 'Supplier SKU'
    variable = True
    help_text = 'The <b>Supplier SKU</b> (Product Code) for the product.'


class Weight(fieldtypes.NumberField):
    label = 'Weight (Grams)'
    name = 'weight'
    required_message = (
        'Please supply a weight. This cannot be blank but can be zero.')
    variable = True
    empty_value = 0
    help_text = 'The <b>Shipping Weight</b> of the product in <b>Grams</b>.'


class Height(fieldtypes.NumberField):
    label = 'Height (Milimeters)'
    name = 'height'
    variable = True
    empty_value = 0
    help_text = (
        'The <b>Height</b> of the item when packed in <b>Milimeters</b>.')


class Width(fieldtypes.NumberField):
    label = 'Width (Milimeters)'
    name = 'width'
    variable = True
    empty_value = 0
    help_text = (
        'The <b>Width</b> of the item when packed in <b>Milimeters</b>.')


class Length(fieldtypes.NumberField):
    label = 'Length (Milimeters)'
    name = 'length'
    variable = True
    empty_value = 0
    help_text = (
        'The <b>Length</b> of the item when packed in <b>Milimeters</b>.')


class PackageType(fieldtypes.ChoiceField):
    label = 'Package Type'
    name = 'package_type'
    variable = True
    required_message = 'A <b>Package Type</b> must be supplied.'
    help_text = (
        'The <b>Shipping Rule</b> will be selected acording to the '
        '<b>Package Type</b>.<br>The <b>International Shipping</b> will also '
        'be set accordingly. If the product cannot be shipped outside the UK '
        'or the <b>International Shippping Method</b> differs, please change '
        'the <b>International Shipping</b> option after the product has been '
        'created.')

    @staticmethod
    def get_choices():
        package_types = [
            (service.value, service.value)
            for service in CCAPI.get_option_values("33852")]
        return [('', '')] + package_types


class Location(fieldtypes.LocationField):
    label = 'Location'
    name = 'location'
    placeholder = 'Location'
    variable = True
    help_text = (
        'The name of the <b>Bay</b> in which the product will be located.'
        '<br>This should be left blank if the product does not have a '
        'specific <b>Bay</b>.<br>If additional bays are required they '
        'must be added after the product has been created.')

    @staticmethod
    def get_choices():
        return [(bay.id, bay) for bay in models.Bay.objects.all()]


class Brand(fieldtypes.TextField):
    label = 'Brand'
    name = 'brand'
    required_message = "Please supply a brand"
    placeholder = 'Brand'
    help_text = (
        'The <b>Brand</b> of the product.<br>This is required for listings.')


class Manufacturer(fieldtypes.TextField):
    label = 'Manufacturer'
    name = 'manufacturer'
    required_message = "Please supply a manufacturer",
    placeholder = 'Manufacturer'
    help_text = (
        'The <b>Manufacturer</b> of the product.<br>This is required for '
        'listings.')


class Gender(fieldtypes.ChoiceField):
    label = 'Gender'
    name = 'gender'
    placeholder = 'Gender'
    variable = True
    help_text = 'Gender for which the product is intended.'
    MENS = 'mens'
    WOMENS = 'womens'
    BOYS = 'boys'
    GIRLS = 'girls'
    BABY_BOYS = 'baby-boys'
    BABY_GIRLS = 'baby-girls'
    UNISEX_BABY = 'unisex-baby'

    def get_choices(self):
        return (
            (None, ''),
            (self.MENS, 'Mens'),
            (self.WOMENS, 'Womens'),
            (self.BOYS, 'Boys'),
            (self.GIRLS, 'Girls'),
            (self.BABY_BOYS, 'Baby Boys'),
            (self.BABY_GIRLS, 'Baby Girls'),
            (self.UNISEX_BABY, 'Unisex Baby'))


class MetaFormFields(type):

    def __iter__(self):
        for field in self.fields:
            yield field


class DeleteVariation(fieldtypes.CheckboxField):

    label = 'Delete'
    html_class = 'delete_variation'
    help_text = (
        'Select this option for variations that do not exist or we will not '
        'stock.')


class ListOption(fieldtypes.FormField, ListInput):

    separator = '|'
    disallowed_characters = [separator]

    def prepare_value(self, value):
        if value is None:
            return json.dumps([])
        if value[0] == '[':
            return value
        return json.dumps(value.split(self.separator))

    def clean(self, value):
        if value is None:
            return []
        value = json.loads(value)
        return self.separator.join(value)


class AmazonBulletPoints(ListOption):

    label = 'Amazon Bullet Points'
    name = 'amazon_bullet_points'
    html_class = 'amazon_bullet_points'
    help_text = 'Create upto five bullet points for Amazon listings.'
    maximum = 5


class AmazonSearchTerms(ListOption):

    label = 'Amazon Search Terms'
    name = 'amazon_search_terms'
    html_class = 'amazon_search_terms'
    help_text = 'Create upto five search terms for Amazon listings.'
    maximum = 5


class FormFields(metaclass=MetaFormFields):
    fields = [
        Title,
        Barcode,
        PurchasePrice,
        VATRate,
        Price,
        StockLevel,
        Department,
        Location,
        Supplier,
        SupplierSKU,
        Weight,
        Height,
        Width,
        Length,
        PackageType,
        Brand,
        Manufacturer,
        Description,
        Gender,
        AmazonBulletPoints,
        AmazonSearchTerms,
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
