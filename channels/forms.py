"""Forms for the channels app."""

from django import forms
from django.core.validators import RegexValidator


class CreateOrder(forms.Form):
    """Form for creating orders."""

    required_css_class = "required"

    company_name = forms.CharField(required=False)
    customer_name = forms.CharField()
    country = forms.CharField(widget=forms.TextInput(attrs={"list": "countries"}))
    post_code = forms.CharField()
    town = forms.CharField()
    address_line_1 = forms.CharField()
    address_line_2 = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="A valid phone number must be entered",
    )
    phone_number = forms.CharField(
        validators=[phone_regex], max_length=17, required=False
    )
    sale_price = forms.FloatField(required=False)
    shipping_price = forms.FloatField(min_value=0)
    basket = forms.CharField(widget=forms.HiddenInput())

    def clean_shipping_price(self):
        """Round the shipping priced to two decimal places."""
        value = self.cleaned_data["shipping_price"]
        return round(value, 2)

    def __init__(self, *args, **kwargs):
        """Set the channel."""
        self.channel = kwargs.pop("channel")
        super().__init__(*args, **kwargs)
