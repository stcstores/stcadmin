from django import forms

from stcadmin import settings

from ccapi import CCAPI


CCAPI.create_session(settings.CC_LOGIN, settings.CC_PWD)


class MetaFormFields(type):

    def __iter__(self):
        for field in self.fields:
            yield field


class MetaFormField(type):

    @property
    def is_required(self):
        if len(self.required_message) > 0:
            return True
        return False


class FormField(metaclass=MetaFormField):

    label = None
    name = None
    field = None
    variable = False
    variation = False
    option = False
    help_text = None
    placeholder = None
    html_class = None
    size = 50
    initial = None
    required_message = ''
    option = False

    @classmethod
    def get_widget(cls):
        attrs = {}
        if cls.placeholder is not None:
            attrs['placeholder'] = cls.placeholder
        if cls.html_class is not None:
            attrs['class'] = cls.html_class
        if cls.size is not None:
            attrs['size'] = cls.size
        return cls.widget_class(attrs=attrs)

    @classmethod
    def field(cls):
        error_messages = None
        if cls.is_required:
            error_messages = {'required': cls.required_message}
        widget = cls.get_widget()
        field = cls.form_class(
            required=cls.is_required, label=cls.label,
            error_messages=error_messages,
            widget=widget, initial=cls.initial,
            help_text=cls.help_text)
        return field


class ChoiceField(FormField):

    form_class = forms.ChoiceField
    widget_class = forms.Select

    @classmethod
    def get_widget(cls):
        return cls.widget_class()

    @classmethod
    def field(self):
        return self.form_class(
            choices=self.get_choices(), label=self.label,
            widget=self.get_widget())


class NumberField(FormField):

    form_class = forms.IntegerField
    widget_class = forms.NumberInput


class PriceField(FormField):
    form_class = forms.FloatField
    widget_class = forms.NumberInput


class TextField(FormField):
    form_class = forms.CharField
    widget_class = forms.TextInput


class TextareaField(FormField):
    form_class = forms.CharField
    widget_class = forms.Textarea


class OptionField(TextField):

    option = True
    variable = True
    variation = True

    def __init__(self, option):
        self.label = option
        self.name = 'opt_{}'.format(option)

    def select_field(self):
        choices = [
            ('{}_unused'.format(self.name), 'Unused'.format(self.name)),
            ('{}_variable'.format(self.name), 'Variable'.format(self.name)),
            ('{}_variation'.format(self.name), 'Variation'.format(self.name))]
        field = forms.ChoiceField(
            label=self.label, widget=forms.RadioSelect,
            choices=choices, initial='{}_unused'.format(self.name))
        return field


class Title(TextField):
    label = 'Title'
    name = 'title'
    required_message = "Please supply a range title"
    placeholder = 'Title'


class Description(TextareaField):
    label = 'Description'
    name = 'description'
    placeholder = 'Description. Will default to title if left blank'


class Barcode(TextField):
    label = 'Barcode'
    name = 'barcode'
    required_message = "Please supply a barcode"
    placeholder = 'Barcode'
    variable = True


class Department(ChoiceField):
    label = 'Department'
    name = 'department'
    placeholder = 'Description. Will default to title if left blank'

    @staticmethod
    def get_choices():
        return [
            (dept.value, dept.value) for dept in
            CCAPI.get_option_values("34325")]


class Price(PriceField):
    label = 'Price (ex VAT)'
    name = 'price'
    required_message = "Please supply a price"
    placeholder = 'Price without shipping or VAT'
    variable = True


class PurchasePrice(PriceField):
    label = 'Purchase Price'
    name = 'purchase_price'
    initial = 0,
    required_message = 'Please provide a stock level. This can be zero.'
    variable = True


class StockLevel(NumberField):
    label = 'Stock Level'
    name = 'stock_level'
    initial = 0
    required_message = 'Please provide a stock level. This can be zero.'
    variable = True


class VATRate(ChoiceField):
    label = 'VAT Rate'
    name = 'vat_rate'
    variable = True

    @staticmethod
    def get_choices():
        return ([
            (5, 'Normal Rate 20%'), (2, 'Reduced 5%'), (1, 'VAT Exempt')])


class Supplier(ChoiceField):
    label = 'Supplier'
    name = 'supplier'

    @staticmethod
    def get_choices():
        suppliers = [
            (supplier.value, supplier.value) for supplier in
            CCAPI.get_option_values("35131")]
        suppliers.sort(key=lambda x: x[1])
        return suppliers


class SupplierSKU(TextField):
    label = 'Supplier SKU'
    name = 'supplier_SKU'
    placeholder = 'Supplier SKU'
    variable = True


class Weight(NumberField):
    label = 'Weight (Grams)'
    name = 'weight'
    required_message = "Please supply a weight"
    variable = True


class Height(NumberField):
    label = 'Height (Milimeters)'
    name = 'height'
    variable = True


class Width(NumberField):
    label = 'Width (Milimeters)'
    name = 'width'
    variable = True


class Length(NumberField):
    label = 'Length (Milimeters)'
    name = 'length'
    variable = True


class PackageType(ChoiceField):
    label = 'Package Type'
    name = 'package_type'
    variable = True

    @staticmethod
    def get_choices():
        return [
            (service.value, service.value)
            for service in CCAPI.get_option_values("33852")]


class Location(TextField):
    label = 'Location'
    name = 'location'
    placeholder = 'Location'
    variable = True


class Brand(TextField):
    label = 'Brand'
    name = 'brand'
    required_message = "Please supply a brand"
    placeholder = 'Brand'


class Manufacturer(TextField):
    label = 'Manufacturer'
    name = 'manufacturer'
    required_message = "Please supply a manufacturer",
    placeholder = 'Manufacturer'


class FormFields(metaclass=MetaFormFields):
    fields = [
        Title,
        Description,
        Barcode,
        Department,
        Price,
        PurchasePrice,
        StockLevel,
        VATRate,
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

    @staticmethod
    def get_options():
        return [
            OptionField(option.option_name) for option in
            CCAPI.get_product_options() if option.exclusions['tesco'] is False]

    fields += get_options.__func__()
