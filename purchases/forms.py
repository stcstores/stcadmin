"""Forms for the purchases app."""

import calendar

from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from channels.models import Channel
from purchases import models


class PurchaseFromStock(forms.Form):
    """Form for creating stock purchases."""

    purchaser = forms.ModelChoiceField(
        queryset=get_user_model().objects.filter(groups__name="purchase")
    )
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
        years = set(models.Purchase.objects.values_list("created_at__year", flat=True))
        self.fields["year"] = forms.IntegerField(
            widget=forms.Select(choices=((year, year) for year in years))
        )
