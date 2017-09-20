from django import forms
from .new_product.fields import Title, Description


class ProductRangeForm(forms.Form):
    end_of_line = forms.BooleanField(required=False)


class DescriptionForm(forms.Form):
    title = Title()
    description = Description()


class ProductForm(forms.Form):
    stock_level = forms.DecimalField()
    weight = forms.DecimalField(help_text='Product Weight in Grams')
    height = forms.DecimalField(help_text='Product height in Centimeters')
    length = forms.DecimalField(help_text='Product length in Centimeters')
    width = forms.DecimalField(help_text='Product width in Centimeters')
