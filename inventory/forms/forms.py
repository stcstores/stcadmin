from django import forms

from .new_product import fields
from .new_product.fields import Description, Title


class ProductRangeForm(forms.Form):
    end_of_line = forms.BooleanField(required=False)


class DescriptionForm(forms.Form):
    title = Title()
    description = Description()
    amazon_bullets = fields.AmazonBulletPoints()
    search_terms = fields.AmazonSearchTerms()
