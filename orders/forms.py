"""Forms for print audit app."""
import calendar
from datetime import datetime

from django import forms
from django.utils import timezone

from home.models import Staff
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

    order_id = forms.CharField(required=False)
    country = forms.ModelChoiceField(
        Country.objects.all().order_by("name"), required=False
    )
    channel = forms.ModelChoiceField(
        models.Channel.objects.all().order_by("name"), required=False
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

    def clean_recieved_from(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["recieved_from"]
        if date is not None:
            return timezone.make_aware(datetime.combine(date, datetime.min.time()))

    def clean_recieved_to(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["recieved_to"]
        if date is not None:
            return timezone.make_aware(datetime.combine(date, datetime.max.time()))

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        kwargs = {
            "country": data.get("country"),
            "channel": data.get("channel"),
            "recieved_at__gte": data.get("recieved_from"),
            "recieved_at__lte": data.get("recieved_to"),
            "order_id": data.get("order_id") or None,
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
        return (
            qs.order_by("-recieved_at")
            .prefetch_related("productsale_set")
            .select_related(
                "shipping_service",
                "channel",
                "country",
                "country__region",
            )
            .distinct()
        )


class PackingMistakeForm(forms.ModelForm):
    """Form for packing mistakes."""

    class Meta:
        """Meta class for Packing Mistake Form."""

        model = models.PackingMistake
        fields = ["user", "timestamp", "order_id", "note"]
        widgets = {"timestamp": forms.DateInput(attrs={"class": "datepicker"})}

    def __init__(self, *args, **kwargs):
        """Set the user queryset."""
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = Staff.unhidden.all()


class PackCountFilter(forms.Form):
    """Form for filtering packing counts."""

    month = forms.ChoiceField()
    year = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        """Set choices."""
        super().__init__(*args, **kwargs)
        now = timezone.now()
        self.fields["month"].choices = (
            (i, month) for i, month in enumerate(calendar.month_name[1:], 1)
        )
        self.fields["year"].choices = (
            (year, str(year))
            for year in reversed(
                sorted(
                    models.Order.objects.filter(dispatched_at__isnull=False)
                    .values_list("dispatched_at__year", flat=True)
                    .distinct()
                )
            )
        )
        self.initial = {"year": now.year, "month": now.month}


class PackingMistakeFilterForm(forms.Form):
    """Form for filtering packing mistakes."""

    user = forms.ChoiceField(required=False)
    made_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    made_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    def __init__(self, *args, **kwargs):
        """Set choices."""
        super().__init__(*args, **kwargs)
        self.fields["user"].choices = [("", "Any")] + [
            (_.id, str(_)) for _ in Staff.unhidden.all()
        ]

    def clean_made_from(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["made_from"]
        if date is not None:
            return timezone.make_aware(datetime.combine(date, datetime.min.time()))

    def clean_made_to(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["made_to"]
        if date is not None:
            return timezone.make_aware(datetime.combine(date, datetime.max.time()))

    def get_queryset(self):
        """Return a queryset with filters."""
        if self.is_valid():
            data = self.cleaned_data
            qs = models.PackingMistake.objects.all()
            if user := data["user"]:
                qs = qs.filter(user=user)
            if made_from := data["made_from"]:
                qs = qs.filter(timestamp__gte=made_from)
            if made_to := data.get("made_to"):
                qs = qs.filter(timestamp__lte=made_to)
            return qs
        raise Exception("Form Invalid")
