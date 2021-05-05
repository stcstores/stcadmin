"""Forms for the purchases app."""

import calendar

from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from channels.models import Channel
from purchases import models
from shipping.models import Country, ShippingPrice, ShippingService


class DiscountField(forms.TypedChoiceField):
    """Field for selecting purchase discount amount."""

    discount_values = ((50, "50%"), (20, "20%"), (0, "No Discount"))

    def __init__(self, *args, **kwargs):
        """Field for selecting purchase discount amount."""
        kwargs["coerce"] = int
        kwargs["choices"] = self.discount_values
        super().__init__(*args, **kwargs)


class PurchaseFromStock(forms.Form):
    """Form for creating stock purchases."""

    purchaser = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name="purchase")
    )
    discount = DiscountField()
    basket = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        """Add the selling channel to the form."""
        super().__init__(*args, **kwargs)
        self.channel = get_object_or_404(Channel, name="Telephone Channel")


class PurchaseManagement(forms.Form):
    """Form for filtering purchases."""

    MONTHS = list(enumerate(calendar.month_name[1:], 1))

    month = forms.IntegerField(widget=forms.Select(choices=MONTHS))
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name="purchase")
    )

    def __init__(self, *args, **kwargs):
        """Set the month select fields."""
        super().__init__(*args, **kwargs)
        years = set(
            models.Purchase.objects.filter(cancelled=False).values_list(
                "created_at__year", flat=True
            )
        )
        self.fields["year"] = forms.IntegerField(
            widget=forms.Select(choices=((year, year) for year in years))
        )


class PurchaseShipping(forms.Form):
    """Form for purchasing shipping."""

    purchaser = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name="purchase")
    )
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    shipping_service = forms.ModelChoiceField(
        queryset=ShippingService.objects.filter(
            shippingprice__inactive=False
        ).distinct()
    )
    weight = forms.IntegerField()

    def clean(self):
        """Add the shipping price to the form data."""
        cleaned_data = super().clean()
        shipping_price = ShippingPrice.objects.get(
            country=cleaned_data["country"],
            shipping_service=cleaned_data["shipping_service"],
            inactive=False,
        )
        cleaned_data["shipping_price"] = shipping_price
        cleaned_data["price"] = shipping_price.price(cleaned_data["weight"])
        return cleaned_data
