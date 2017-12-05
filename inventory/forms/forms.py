from django import forms

from .new_product import fields
from .new_product.fields import Description, Title


class ProductRangeForm(forms.Form):
    end_of_line = forms.BooleanField(
        required=False,
        help_text=(
            'Ranges are maked as <b>end of line</b> if the entire range is'
            ' out of stock and unlikely to be re-ordered.'))


class DescriptionForm(forms.Form):
    title = Title()
    description = Description()
    amazon_bullets = fields.AmazonBulletPoints()
    search_terms = fields.AmazonSearchTerms()
