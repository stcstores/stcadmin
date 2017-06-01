from django import forms

DEPARTMENTS = [(d, d) for d in ['Sureware', 'Allsorts', 'Country Gifts', 'Sports Shop', 'Warehouse', 'Containers', 'Trelawney Attic', 'Top to Toe']] # Get from CC
VAT_RATES = ([(0.2, 'Normal Rate 20%'), (0.05, 'Reduced 5%'), (0, 'VAT Exempt')]) # Get from CC?
SUPPLIERS = [(d, d) for d in ['Baum Trading', 'KS Brands', 'Kandy Toys']] # Get from CC
PACKAGE_TYPES = enumerate(['Packet', 'Large Letter', 'Heavy and Large', 'Courier']) # Get from CC
OPTIONS = [
    'Design', 'Colour', 'Size', 'Quantity', 'Weight', 'Strength', 'Calibre',
    'Scent', 'Name', 'Finish', 'Word', 'Model']

text_input_size = 50


class NewProductFormField:

    def __new__(
            self, required_message=None, size=50, placeholder=None,
            html_class='new_product_input', textarea=False):
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
            required=required, error_messages=error_messages,
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
cost_price = TextField(
    required_message="Please supply a price", placeholder='Cost Price')
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

    def __new__(self, placeholder):
        return TextField(placeholder=placeholder)


option_fields = [(option, OptionField(option)) for option in OPTIONS]
