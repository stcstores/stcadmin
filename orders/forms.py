"""Forms for print audit app."""
from datetime import datetime

from django import forms
from django.utils.timezone import make_aware

from orders import models
from shipping.models import Country


class ChartSettingsForm(forms.Form):
    """Form for setting options for Charts."""

    number_of_weeks = forms.IntegerField(
        min_value=10, max_value=250, widget=forms.NumberInput(attrs={"step": "10"})
    )


class OrderListFilter(forms.Form):
    """Form for filtering the shipping method list."""

    order_ID = forms.CharField(required=False)
    country = forms.ModelChoiceField(Country.objects.all(), required=False)
    recieved_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    recieved_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    def clean_recieved_from(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["recieved_from"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.min.time()))

    def clean_recieved_to(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["recieved_to"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.max.time()))

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        kwargs = {
            "country": data.get("country"),
            "recieved_at__gte": data.get("recieved_from"),
            "recieved_at__lte": data.get("recieved_to"),
            "order_ID": data.get("order_ID") or None,
        }
        return {key: value for key, value in kwargs.items() if value is not None}

    def get_queryset(self):
        """Return a queryset of orders based on the submitted data."""
        kwargs = self.query_kwargs(self.cleaned_data)
        return models.Order.dispatched.filter(**kwargs).order_by("-recieved_at")
