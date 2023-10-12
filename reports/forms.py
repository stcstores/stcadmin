"""Forms for the reports app."""

import datetime as dt

from django import forms
from django.utils.timezone import make_aware

from inventory.models import Supplier


class ReorderReportForm(forms.Form):
    """Form for creating reorder reports."""

    supplier = forms.ModelChoiceField(queryset=Supplier.objects.active())
    date_from = forms.DateField(widget=forms.DateInput(attrs={"class": "datepicker"}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={"class": "datepicker"}))

    def clean(self):
        """Make date range timezone aware."""
        cleaned_data = super().clean()
        cleaned_data["date_from"] = self.convert_date(cleaned_data["date_from"])
        cleaned_data["date_to"] = self.convert_date(cleaned_data["date_to"])
        return cleaned_data

    def convert_date(self, date):
        """Return a datetime.date as a timezone aware datetime.datetime."""
        return make_aware(dt.datetime.combine(date, dt.datetime.min.time()))
