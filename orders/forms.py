"""Forms for print audit app."""
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware

from orders import models
from shipping.models import Country
from stcadmin.forms import KwargFormSet


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
        return (
            models.Order.objects.dispatched().filter(**kwargs).order_by("-recieved_at")
        )


class RefundListFilter(forms.Form):
    """Form for filtering the refund list."""

    order_ID = forms.CharField(required=False)
    product_SKU = forms.CharField(required=False)
    dispatched_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    dispatched_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    def clean_dispatched_from(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["dispatched_from"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.min.time()))

    def clean_dispatched_to(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["dispatched_to"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.max.time()))

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        kwargs = {
            "order__dispatched__gte": data.get("recieved_from"),
            "order__dispatched_at__lte": data.get("recieved_to"),
            "order__order_ID": data.get("order_ID") or None,
        }
        return {key: value for key, value in kwargs.items() if value is not None}

    def get_queryset(self):
        """Return a queryset of orders based on the submitted data."""
        kwargs = self.query_kwargs(self.cleaned_data)
        return models.Refund.objects.filter(**kwargs).order_by("-order__dispatched_at")


class CreateRefund(forms.Form):
    """Form for selecting an order for which a refund will be created."""

    BROKEN = "broken"
    PACKING_MISTAKE = "packing_mistake"
    LINKING_MISTAKE = "linking_mistake"
    LOST_IN_POST = "lost_in_post"
    DEMIC = "demic"

    refund_types = {
        BROKEN: models.BreakageRefund,
        PACKING_MISTAKE: models.PackingMistakeRefund,
        LINKING_MISTAKE: models.LinkingMistakeRefund,
        LOST_IN_POST: models.LostInPostRefund,
        DEMIC: models.DemicRefund,
    }

    order_ID = forms.CharField()
    refund_type = forms.ChoiceField(
        choices=(
            (BROKEN, "Broken - An item was broken when in transit"),
            (PACKING_MISTAKE, "Packing Mistake - The wrong item was sent"),
            (
                LINKING_MISTAKE,
                "Linking Mistake - The wrong item was sent due to a linking error",
            ),
            (LOST_IN_POST, "Lost in Post - The item never arrived"),
            (DEMIC, "Demic - We recieved the item in an unsalable state"),
        ),
        widget=forms.RadioSelect(),
    )

    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        try:
            cleaned_data["order"] = models.Order.objects.get(
                order_ID=cleaned_data["order_ID"]
            )
        except models.Order.DoesNotExist:
            raise ValidationError("Order not found")
        return cleaned_data


class RefundProductSelectForm(forms.Form):
    """Form for adding products to a refund."""

    product_sale_id = forms.CharField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=0)

    def __init__(self, *args, **kwargs):
        """Set the initial and max quantity."""
        self.product_sale = kwargs.pop("product_sale")
        super().__init__(*args, **kwargs)
        self.fields["quantity"].max_value = self.product_sale.quantity
        self.initial = self.get_initial()

    def get_initial(self):
        """Return the initial values for the form."""
        return {
            "product_sale_id": self.product_sale.id,
            "quantity": self.product_sale.quantity,
        }


class RefundProductFormset(KwargFormSet):
    """Form set for adding products to refunds."""

    form = RefundProductSelectForm
