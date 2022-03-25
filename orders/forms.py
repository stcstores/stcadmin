"""Forms for print audit app."""
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.timezone import make_aware

from inventory.models import Supplier
from orders import models
from shipping.models import Country, Region
from stcadmin.forms import KwargFormSet
from tracking.models import TrackingCarrier


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
            "channel": data.get("channel"),
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
            .prefetch_related("productsale_set")
            .select_related(
                "shipping_rule",
                "courier_service",
                "channel",
                "country",
                "country__region",
            )
            .distinct()
        )


class RefundListFilter(forms.Form):
    """Form for filtering the refund list."""

    ANY = "any"
    YES = "yes"
    NO = "no"
    BOOLEAN_CHOICES = ((ANY, ""), (YES, "Yes"), (NO, "No"))

    BREAKAGE = "breakage"
    PACKING = "packing"
    LINKING = "linking"
    LOST = "lost"
    DEMIC = "demic"

    TYPE_CHOICES = (
        ("", "Any"),
        (BREAKAGE, "Breakage"),
        (PACKING, "Packing Mistake"),
        (LINKING, "Linking Mistake"),
        (LOST, "Lost in Post"),
        (DEMIC, "Demic"),
    )

    REFUND_TYPES = {
        BREAKAGE: models.BreakageRefund,
        PACKING: models.PackingMistakeRefund,
        LINKING: models.LinkingMistakeRefund,
        LOST: models.LostInPostRefund,
        DEMIC: models.DemicRefund,
    }
    search = forms.CharField(required=False)
    order_ID = forms.CharField(required=False)
    product_SKU = forms.CharField(required=False)
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), required=False)
    dispatched_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    dispatched_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    created_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    created_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    refund_type = forms.ChoiceField(choices=TYPE_CHOICES, required=False)
    contacted = forms.ChoiceField(choices=BOOLEAN_CHOICES, required=False)
    accepted = forms.ChoiceField(choices=BOOLEAN_CHOICES, required=False)
    closed = forms.ChoiceField(choices=BOOLEAN_CHOICES, required=False)

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

    def clean_created_from(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["created_from"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.min.time()))

    def clean_created_to(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["created_to"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.max.time()))

    def clean_contacted(self):
        """Return selection an bool or None."""
        value = self.cleaned_data["contacted"]
        if value == self.YES:
            return True
        elif value == self.NO:
            return False
        return None

    def clean_accepted(self):
        """Return selection an bool or None."""
        value = self.cleaned_data["accepted"]
        if value == self.YES:
            return True
        elif value == self.NO:
            return False
        return None

    def clean_closed(self):
        """Return selection an bool or None."""
        value = self.cleaned_data["closed"]
        if value == self.YES:
            return True
        elif value == self.NO:
            return False
        return None

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        kwargs = {
            "order__dispatched_at__gte": data.get("dispatched_from"),
            "order__dispatched_at__lte": data.get("dispatched_to"),
            "created_at__gte": data.get("created_from"),
            "created_at__lte": data.get("created_to"),
            "order__order_ID": data.get("order_ID") or None,
            "products__product__sku": data.get("product_SKU") or None,
            "products__product__supplier": data.get("supplier") or None,
            "closed": data.get("closed"),
        }
        return {key: value for key, value in kwargs.items() if value is not None}

    def get_queryset(self):
        """Return a queryset of orders based on the submitted data."""
        kwargs = self.query_kwargs(self.cleaned_data)
        qs = models.Refund.objects.filter(**kwargs).order_by("-order__dispatched_at")
        search_text = self.cleaned_data.get("search")
        if search_text:
            search_text = search_text.strip()
            product_qs = models.ProductRefund.objects.filter(
                Q(product__sku__icontains=search_text)
                | Q(product__name__icontains=search_text)
                | Q(product__supplier__name__icontains=search_text)
            ).values_list("refund", flat=True)
            qs = qs.filter(id__in=product_qs)
        refund_type = self.cleaned_data.get("refund_type")
        if refund_type:
            qs = qs.instance_of(self.REFUND_TYPES[refund_type])
        contacted = self.cleaned_data.get("contacted")
        if contacted is not None:
            qs = qs.filter(Q(ContactRefund___contact_contacted=contacted))
        accepted = self.cleaned_data.get("accepted")
        if accepted is not None:
            qs = qs.filter(Q(ContactRefund___refund_accepted=accepted))
        return qs


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
            (BROKEN, "Broken - An order was damaged in transit"),
            (
                PACKING_MISTAKE,
                "Packing Mistake - The wrong item was sent due to a packing error",
            ),
            (
                LINKING_MISTAKE,
                "Linking Mistake - The wrong item was sent due to a linking error",
            ),
            (LOST_IN_POST, "Lost in Post - An order went missing in transit"),
            (
                DEMIC,
                "Demic - An item was recived from a supplier in an unsalable state",
            ),
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


class TrackingWarningFilter(forms.Form):
    """Form for filtering tracking warnings."""

    region = forms.ModelChoiceField(Region.objects.all(), required=False)
    order_ID = forms.CharField(required=False)
    tracking_number = forms.CharField(required=False)
    carrier = forms.ModelChoiceField(TrackingCarrier.objects.all(), required=False)
    dispatched_after = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    dispatched_before = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )

    def clean_dispatched_after(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["dispatched_after"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.min.time()))

    def clean_dispatched_before(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["dispatched_before"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.max.time()))

    def clean(self):
        """Add filter kwargs."""
        cleaned_data = super().clean()
        self.filter_kwargs = {
            "order__country__region": cleaned_data["region"],
            "order__order_ID": cleaned_data["order_ID"],
            "order__tracking_number": cleaned_data["tracking_number"],
            "carrier": cleaned_data["carrier"],
            "order__dispatched_at__gte": cleaned_data["dispatched_after"],
            "order__dispatched_at__lte": cleaned_data["dispatched_before"],
        }
        self.filter_kwargs = {
            key: value for key, value in self.filter_kwargs.items() if value
        }
        return cleaned_data
