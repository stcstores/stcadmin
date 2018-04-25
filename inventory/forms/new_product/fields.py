"""Fields for use with forms for creating and editing products."""

import json
import re

from ccapi import CCAPI
from django import forms
from django.core.exceptions import ValidationError
from list_input import ListInput

from inventory import models
from inventory.forms import widgets

from . import fieldtypes
from .fieldtypes import Validators


class Title(fieldtypes.TextField):
    """Product Range Title field."""

    label = 'Title'
    name = 'title'
    required_message = "Please supply a range title"
    placeholder = 'Title'
    validators = [Validators.limit_characters(('%', "'"))]
    help_text = (
        "The title for the product.<br>This applies to the "
        "Product Range and all of it's Products.")
    size = 60


class Description(fieldtypes.TextareaField):
    """Field for editing product descriptions."""

    required = False
    label = 'Description'
    name = 'description'
    html_class = 'froala'
    placeholder = 'Description. Will default to title if left blank'
    disallowed_characters = ['~']
    help_text = (
        'The Description for the listings.<br>'
        'This can be changed on a channel by channel basis if necessary<br>'
        'If left blank the description will duplicate the title.<br>'
        'For variation items the description applies to the range as a whole.')

    def clean(self, value):
        """Remove invalid characters."""
        value = super().clean(value)
        value = value.replace('&nbsp;', ' ')  # Remove Non breaking spaces
        value = re.sub(' +', ' ', value)  # Remove multiple space characters
        return value


class Barcode(fieldtypes.TextField):
    """Field for product barcodes."""

    label = 'Barcode'
    name = 'barcode'
    placeholder = 'Barcode'
    validators = [Validators.numeric]
    must_vary = True
    help_text = (
        "A unique barcode for the product.<br>"
        "If left blank one will be provided from stock.")


class VATRate(fieldtypes.ChoiceField):
    """Field for VAT rates."""

    label = 'VAT Rate'
    name = 'vat_rate'
    variable = True
    help_text = 'The VAT rate that is applicable to the product.'
    required_message = (
        'Please specify the appropriate <b>VAT Rate</b> for the '
        'product.')

    @staticmethod
    def get_choices():
        """Return choice values."""
        return ([
            ('', ''), (20, 'Normal Rate 20%'), (5, 'Reduced 5%'),
            (0, 'VAT Exempt')])


class Price(fieldtypes.PriceField):
    """Field for product price."""

    label = 'Price'
    name = 'price'
    required_message = (
        'Please provide a <b>Price</b>. This cannot be blank but can be zero.')
    help_text = (
        'Price <b>without shipping</b>.'
        '<br>Ex VAT cannot be blank but can be zero.')
    variable = True


class VATPrice(fieldtypes.CombinationField):
    """Combined field for VAT rate and price."""

    label = 'Price'
    name = 'vat_price'
    required = True
    required_message = ('Please provide a <b>VAT rate</b> and <b>Price</b>.')
    help_text = (
        'Please provide a <b>VAT rate</b> and <b>Price</b>.<br>'
        'The ex VAT price cannot be blank but can be zero.')

    def __init__(self, *args, **kwargs):
        """Create fields."""
        kwargs['label'] = 'Price'
        fields = (
            forms.ChoiceField(
                required=True,
                choices=widgets.VATPriceWidget.vat_choices()),
            forms.FloatField(required=True),
            forms.FloatField(required=True))
        kwargs['widget'] = widgets.VATPriceWidget()
        super().__init__(
            fields=fields, require_all_fields=True, *args, **kwargs)

    def compress(self, data_list):
        """Return submitted values as a dict."""
        vat_rate, ex_vat_price, with_vat_price = data_list
        return {
            'vat_rate': vat_rate, 'ex_vat': ex_vat_price,
            'with_vat_price': with_vat_price}


class PurchasePrice(fieldtypes.PriceField):
    """Field for purchase prices."""

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
    """Field for stock level."""

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


class Supplier(fieldtypes.SingleSelectize):
    """Field for selecting the supplier of a product."""

    label = 'Supplier'
    name = 'supplier'
    html_class = 'selectize'
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
        """Return field choices."""
        factories = CCAPI.get_factories()
        suppliers = [(f.name, f.name) for f in factories]
        suppliers.sort(key=lambda x: x[1])
        return [('', '')] + suppliers


class SupplierSKU(fieldtypes.TextField):
    """Field for Supplier SKU."""

    label = 'Supplier SKU'
    name = 'supplier_SKU'
    placeholder = 'Supplier SKU'
    variable = True
    help_text = 'The <b>Supplier SKU</b> (Product Code) for the product.'


class Weight(fieldtypes.NumberField):
    """Field for the weight of the product."""

    label = 'Weight (Grams)'
    name = 'weight'
    required_message = (
        'Please supply a weight. This cannot be blank but can be zero.')
    variable = True
    empty_value = 0
    help_text = 'The <b>Shipping Weight</b> of the product in <b>Grams</b>.'


class Height(fieldtypes.NumberField):
    """Field for the height of the product."""

    label = 'Height (Milimeters)'
    name = 'height'
    variable = True
    empty_value = 0
    help_text = (
        'The <b>Height</b> of the item when packed in <b>Milimeters</b>.')


class Width(fieldtypes.NumberField):
    """Field for the width of the product."""

    label = 'Width (Milimeters)'
    name = 'width'
    variable = True
    empty_value = 0
    help_text = (
        'The <b>Width</b> of the item when packed in <b>Milimeters</b>.')


class Length(fieldtypes.NumberField):
    """Field for the length of the product."""

    label = 'Length (Milimeters)'
    name = 'length'
    variable = True
    empty_value = 0
    help_text = (
        'The <b>Length</b> of the item when packed in <b>Milimeters</b>.')


class PackageType(fieldtypes.SingleSelectize):
    """Field for selecting the package type of a product."""

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
    selectize_options = {'maxItems': 1}

    @staticmethod
    def get_choices():
        """Return choices for field."""
        package_types = [
            (service.value, service.value)
            for service in CCAPI.get_option_values("33852")]
        return [('', '')] + package_types


class Department(fieldtypes.SingleSelectize):
    """Field for product department."""

    label = 'Department'
    name = 'department'
    required_message = "A <b>Department</b> must be selected."
    help_text = (
        'The <b>Department</b> to which the product belongs.')

    @staticmethod
    def get_choices():
        """Get choice options for field."""
        departments = [
            (w.warehouse_id, w.name) for w in
            models.Warehouse.used_warehouses.all()]
        departments.sort(key=lambda x: x[1])
        return [('', '')] + departments

    def clean(self, value):
        """Validate cleaned data."""
        value = super().clean(value)
        if self.required is False and value == '':
            return None
        try:
            department = models.Warehouse.used_warehouses.get(
                warehouse_id=int(value)).name
        except models.Warehouse.DoesNotExist:
            raise forms.ValidationError('Deparment not recognised')
        return department


class Location(fieldtypes.SelectizeField):
    """Field for choosing warehouse bays."""

    label = 'Location'
    name = 'location'
    placeholder = 'Location'
    variable = True
    html_class = 'location_field'
    required = False
    help_text = (
        'The name of the <b>Bay</b> in which the product will be located.'
        '<br>This should be left blank if the product does not have a '
        'specific <b>Bay</b>.<br>If additional bays are required they '
        'must be added after the product has been created.')
    selectize_options = {
        'delimiter': ',',
        'persist': False,
        'maxItems': None,
        'sortField': 'text',
    }

    def __init__(self, department=None):
        """Set department."""
        self.department = department
        super().__init__()

    def get_choices(self):
        """Return choices for field."""
        if self.department is None:
            warehouses = models.Warehouse.used_warehouses.all()
            options = [['', '']]
            for warehouse in warehouses:
                options.append(
                    [warehouse.name, [
                        [bay.id, bay] for bay in warehouse.bay_set.all()]])
            return options
        else:
            try:
                warehouse = self.get_warehouse()
            except models.Warehouse.DoesNotExist:
                return [('', '')]
            else:
                return [(bay.id, bay.name) for bay in warehouse.bay_set.all()]

    def get_warehouse(self):
        """Return Warehouse object matching the field's department."""
        if isinstance(self.department, int):
            return models.Warehouse.objects.get(
                warehouse_id=self.department)
        return models.Warehouse.objects.get(
            name=self.department)

    def to_python(self, *args, **kwargs):
        """Return submitted bays as a list of bay IDs."""
        return [int(x) for x in super().to_python(*args, **kwargs)]

    def clean(self, value):
        """Validate bay selection."""
        value = super().clean(value)
        bays = []
        for bay_id in value:
            try:
                bays.append(models.Bay.objects.get(bay_id=bay_id))
            except models.DoesNotExist:
                raise forms.ValidationError('Bay not recognised')
        bays = [b for b in bays if not b.default]
        if len(set([bay.warehouse for bay in bays])) > 1:
            raise forms.ValidationError(
                'Bays from multiple warehouses selected.')
        value = [b.id for b in bays]
        if self.department is not None and len(value) == 0:
            value = [self.get_warehouse().default_bay.id]
        return value


class DepartmentBayField(fieldtypes.CombinationField):
    """Combined Department and Location fields."""

    help_text = (
        'Set the <b>Department</b> to which the product belongs in the '
        'Department field.<br>'
        'Bays belonging to this department can then be added to the Bay field.'
        '<br>If the bay field is left blank the default bay for the department'
        ' will be added.')

    def __init__(self, *args, **kwargs):
        """Create sub fields."""
        kwargs['label'] = 'Location'
        self.lock_department = kwargs.pop('lock_department', False)
        fields = (Department(), Location())
        choices = [field.get_choices() for field in fields]
        selectize_options = [field.selectize_options for field in fields]
        if self.lock_department:
            selectize_options[0]['readOnly'] = True
        kwargs['widget'] = widgets.DepartmentBayWidget(
            choices=choices, selectize_options=selectize_options,
            lock_department=self.lock_department)
        super().__init__(
            fields=fields, require_all_fields=False, *args, **kwargs)

    def compress(self, value):
        """Return submitted values as a dict."""
        return {'department': value[0], 'bays': value[1]}

    def clean(self, value):
        """Validate submitted values."""
        value = super().clean(value)
        warehouse = models.Warehouse.used_warehouses.get(
            name=value['department'])
        value['department'] = warehouse.id
        if len(value['bays']) == 0:
            value['bays'] = [warehouse.default_bay.id]
        return value


class OptionField:
    """Base field class for editing Product Options."""

    allowed_characters = {
        'Size': ['+', '-', '.', '/', "'", '"'],
        'Weight': ['.'],
        'Strength': ['+', '-', '.'],
        'Material': ['%', ','],
    }

    def __init__(self, *args, **kwargs):
        """Set options for selectize."""
        self.selectize_options['create'] = True
        super().__init__(*args, **kwargs)

    def legal_characters(self, value):
        """Validate all characters in submitted value are alowed."""
        error_message = '{} is not a valid character for {}.'
        allowed_characters = []
        if self.label in self.allowed_characters:
            allowed_characters += self.allowed_characters[self.label]
        for char in value:
            if not char.isalnum() and not char == ' ':
                if char not in allowed_characters:
                    raise ValidationError(
                        error_message.format(char, self.label))

    def valid_value(self, value):
        """Allow values not in choices."""
        return True

    def validate(self, value):
        """Validate submitted value."""
        super().validate(value)
        if isinstance(value, list):
            for v in value:
                self.legal_characters(v)
        else:
            self.legal_characters(value)

    @staticmethod
    def get_choices(option_name, options=None, initial=None):
        """Return choices for field."""
        if not options:
            options = CCAPI.get_product_options()
        values = [value.value for value in options[option_name]]
        if initial and initial not in values:
            values.append(initial)
        return [('', '')] + [(v, v) for v in values]


class VariationOptions(OptionField, fieldtypes.SelectizeField):
    """Field for options that define variations."""

    pass


class ListingOption(OptionField, fieldtypes.SingleSelectize):
    """Field for options that provide information for listings."""

    pass


class Brand(ListingOption):
    """Field for the Brand of the product."""

    label = 'Brand'
    name = 'brand'
    required_message = "Please supply a brand"
    placeholder = 'Brand'
    help_text = (
        'The <b>Brand</b> of the product.<br>This is required for listings.')


class Manufacturer(ListingOption):
    """Field for the manufacturer of the product."""

    label = 'Manufacturer'
    name = 'manufacturer'
    required_message = "Please supply a manufacturer",
    placeholder = 'Manufacturer'
    help_text = (
        'The <b>Manufacturer</b> of the product.<br>This is required for '
        'listings.')


class Gender(fieldtypes.ChoiceField):
    """Field for the gender option of Amazon listings."""

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
        """Return choices for field."""
        return (
            (None, ''),
            (self.MENS, 'Mens'),
            (self.WOMENS, 'Womens'),
            (self.BOYS, 'Boys'),
            (self.GIRLS, 'Girls'),
            (self.BABY_BOYS, 'Baby Boys'),
            (self.BABY_GIRLS, 'Baby Girls'),
            (self.UNISEX_BABY, 'Unisex Baby'))


class ListOption(fieldtypes.FormField, ListInput):
    """Base class for fields based on ListInput."""

    separator = '|'
    disallowed_characters = [separator]

    def clean(self, value):
        """Clean submitted value."""
        if value is None:
            return []
        value = json.loads(value)
        return value


class AmazonBulletPoints(ListOption):
    """Field for Amazon bullet point descriptions."""

    label = 'Amazon Bullet Points'
    name = 'amazon_bullet_points'
    html_class = 'amazon_bullet_points'
    help_text = 'Create upto five bullet points for Amazon listings.'
    maximum = 5


class AmazonSearchTerms(ListOption):
    """Field for Amazon search terms."""

    label = 'Amazon Search Terms'
    name = 'amazon_search_terms'
    html_class = 'amazon_search_terms'
    help_text = 'Create upto five search terms for Amazon listings.'
    maximum = 5
