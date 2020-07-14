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

    DISPATCHED = "dispatched"
    UNDISPATCHED = "undispatched"
    ANY = "any"
    SHOW = "show"
    HIDE = "hide"

    order_ID = forms.CharField(required=False)
    country = forms.ModelChoiceField(
        Country.objects.all().order_by("name"), required=False
    )
    recieved_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    recieved_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    status = forms.ChoiceField(
        choices=(
            (ANY, "Any"),
            (DISPATCHED, "Dispatched"),
            (UNDISPATCHED, "Undispatched"),
        ),
        required=False,
    )
    contains_EOL_items = forms.ChoiceField(
        choices=((ANY, "Any"), (SHOW, "Show"), (HIDE, "Hide")),
        required=False,
        label="Contains EOL Items",
    )
    profit_calculable_only = forms.BooleanField(initial=False, required=False)

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

    def clean_contains_EOL_items(self):
        """Return bool or None."""
        value = self.cleaned_data["contains_EOL_items"]
        if value == self.SHOW:
            return True
        if value == self.HIDE:
            return False
        return None

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
        qs = models.Order.objects.filter(**kwargs)
        if self.cleaned_data.get("status") == self.DISPATCHED:
            qs = qs.dispatched()
        elif self.cleaned_data.get("status") == self.UNDISPATCHED:
            qs = qs.undispatched()
        if self.cleaned_data["profit_calculable_only"] is True:
            qs = qs.profit_calculable()
        if self.cleaned_data["contains_EOL_items"] is True:
            qs = qs.filter(productsale__end_of_line=True).exclude(
                productsale__end_of_line__isnull=True
            )
        elif self.cleaned_data["contains_EOL_items"] is False:
            qs = qs.exclude(productsale__end_of_line=True).exclude(
                productsale__end_of_line__isnull=True
            )
        return (
            qs.order_by("-recieved_at")
            .prefetch_related("productsale_set", "productsale_set__department")
            .select_related(
                "shipping_rule",
                "courier_service",
                "channel",
                "country",
                "country__region",
            )
            .distinct()
        )
