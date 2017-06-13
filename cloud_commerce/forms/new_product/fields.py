from django import forms

from stcadmin import settings

from ccapi import CCAPI


CCAPI.create_session(settings.CC_LOGIN, settings.CC_PWD)


OPTIONS = [
    option.option_name for option in CCAPI.get_product_options() if
    option.exclusions['tesco'] is False]

PACKAGE_TYPES = [
    (service.id, service.value)
    for service in CCAPI.get_option_values("33852")]

DEPARTMENTS = [
    (dept.value, dept.value) for dept in CCAPI.get_option_values("34325")]

VAT_RATES = ([
    (5, 'Normal Rate 20%'), (2, 'Reduced 5%'), (1, 'VAT Exempt')])

SUPPLIERS = [
    (supplier.value, supplier.value) for supplier in CCAPI.get_option_values(
        "35131")]
SUPPLIERS.sort(key=lambda x: x[1])


class NewProductFormField:

    def __new__(
            self, required_message=None, size=50, placeholder=None,
            html_class='new_product_input', textarea=False, label=None):
        if textarea is True:
            widget_class = forms.Textarea
        else:
            widget_class = forms.TextInput
        if required_message is not None:
            required = True
            error_messages = {'required': required_message}
        else:
            required = False
            error_messages = {}
        attrs = {}
        if placeholder is not None:
            attrs['placeholder'] = placeholder
        if html_class is not None:
            attrs['class'] = html_class
        if size is not None:
            attrs['size'] = size
        return self.field_class(
            required=required, label=label, error_messages=error_messages,
            widget=widget_class(attrs=attrs))


class TextField(NewProductFormField):
    field_class = forms.CharField


class NumberField(NewProductFormField):
    field_class = forms.IntegerField


title = TextField(
    required_message="Please supply a range title", placeholder='Title')
description = TextField(
    required_message="Please supply a brief description of the product",
    placeholder='Description', textarea=True)
barcode = TextField(
    required_message="Please supply a barcode", placeholder='Barcode')
department = forms.ChoiceField(choices=DEPARTMENTS)
price = TextField(
    required_message="Please supply a price",
    placeholder='Price without shipping or VAT')
purchase_price = TextField(
    required_message="Please supply a price", placeholder='Purchase Price')
vat_rate = forms.ChoiceField(choices=VAT_RATES)
supplier = forms.ChoiceField(choices=SUPPLIERS)
supplier_SKU = TextField(placeholder='Supplier SKU')
weight = NumberField(required_message="Please supply a weight")
height = NumberField()
width = NumberField()
length = NumberField()
package_type = forms.ChoiceField(choices=PACKAGE_TYPES)
location = TextField(placeholder='Location')
brand = TextField(
    required_message="Please supply a brand", placeholder='Brand')
manufacturer = TextField(
    required_message="Please supply a manufacturer",
    placeholder='Manufacturer')


class OptionField:

    def __new__(self, name):
        return TextField(placeholder=name, label=name)


option_fields = [(option, OptionField(option)) for option in OPTIONS]
