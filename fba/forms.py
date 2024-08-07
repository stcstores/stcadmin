"""Forms for the FBA app."""

import datetime as dt
import json
from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.timezone import make_aware, now

from fba import models
from home.models import Staff
from inventory.forms.fieldtypes import SelectizeModelChoiceField
from inventory.models import BaseProduct, ProductRange, Supplier


class SelectFBAOrderProductForm(forms.Form):
    """Form for selecting a product for an FBA order."""

    product_SKU = forms.CharField()

    def clean(self):
        """Add product ID to cleaned data."""
        cleaned_data = super().clean()
        try:
            cleaned_data["product"] = BaseProduct.objects.get(
                sku=cleaned_data["product_SKU"],
                product_range__status=ProductRange.COMPLETE,
            )
        except BaseProduct.DoesNotExist:
            self.add_error("product_SKU", "Product not found")


class CurrencyWidget(forms.TextInput):
    """Widget that converts pence to pounds and pence."""

    def __init__(self, *args, **kwargs):
        """Add attributes."""
        attrs = kwargs.get("attrs", {})
        attrs.update({"type": "number", "step": "0.01"})
        kwargs["attrs"] = attrs
        super().__init__(*args, **kwargs)

    def format_value(self, value):
        """Return the value as pounds."""
        if value == "" or value is None:
            return None
        return str(float(value) / 100).zfill(3)


class CurrencyField(forms.FloatField):
    """Form class for saving currency as an integer."""

    widget_class = CurrencyWidget

    def to_python(self, value):
        """Convert input to an integer."""
        return int(float(value) * 100)


class FBAOrderForm(forms.ModelForm):
    """Form for creating FBA orders."""

    class Meta:
        """Meta class for FBAOrderForm."""

        field_classes = {
            "selling_price": CurrencyField,
            "FBA_fee": CurrencyField,
        }
        model = models.FBAOrder
        exclude = [
            "fulfilled_by",
            "closed_at",
            "box_weight",
            "priority",
            "printed",
            "update_stock_level_when_complete",
            "status",
            "quantity_sent",
            "small_and_light",
            "created_at",
            "is_stopped",
            "stopped_at",
            "stopped_until",
            "stopped_reason",
        ]
        widgets = {
            "product": forms.HiddenInput(),
            "product_weight": forms.HiddenInput(),
            "product_hs_code": forms.HiddenInput(),
            "product_purchase_price": forms.HiddenInput(),
            "tracking_number": forms.HiddenInput(),
            "product_is_multipack": forms.HiddenInput(),
            "selling_price": CurrencyWidget,
            "FBA_fee": CurrencyWidget,
        }

    field_order = [
        "region",
        "product_asin",
        "selling_price",
        "FBA_fee",
        "aproximate_quantity",
        "tracking_number",
        "is_combinable",
        "on_hold",
        "notes",
    ]

    def __init__(self, *args, **kwargs):
        """Form for managing FBA orders."""
        super().__init__(*args, **kwargs)
        if not self.instance.id:
            self.fields["region"].queryset = models.FBARegion.objects.filter(
                active=True
            )


class FBAOrderFilter(forms.Form):
    """Form for filtering the FBA order list."""

    CLOSED = "closed"
    NOT_CLOSED = "not_closed"

    PRIORITISED = "prioritised"
    UNPRIORITISED = "unprioritised"

    search = forms.CharField(required=False)
    status = forms.ChoiceField(
        choices=(
            ("", ""),
            (models.FBAOrder.NOT_PROCESSED, models.FBAOrder.NOT_PROCESSED),
            (models.FBAOrder.PRINTED, models.FBAOrder.PRINTED),
            (models.FBAOrder.READY, models.FBAOrder.READY),
            (models.FBAOrder.FULFILLED, models.FBAOrder.FULFILLED),
            (models.FBAOrder.ON_HOLD, models.FBAOrder.ON_HOLD),
            (models.FBAOrder.STOPPED, models.FBAOrder.STOPPED),
        ),
        required=False,
    )
    created_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "datepicker", "size": "6"}),
    )
    created_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "datepicker", "size": "6"}),
    )
    fulfilled_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "datepicker", "size": "6"}),
    )
    fulfilled_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "datepicker", "size": "6"}),
    )
    fulfilled_by = forms.ModelChoiceField(
        Staff.objects.filter(fba_packer=True, hidden=False).order_by("first_name"),
        required=False,
    )
    country = forms.ModelChoiceField(models.FBARegion.objects.all(), required=False)
    supplier = forms.ChoiceField(choices=[], required=False)
    closed = forms.ChoiceField(
        choices=(("", "---------"), (CLOSED, "Closed"), (NOT_CLOSED, "Not Closed")),
        required=False,
    )
    prioritised = forms.ChoiceField(
        choices=(
            ("", "---------"),
            (PRIORITISED, "Prioritised"),
            (UNPRIORITISED, "Unprioritised"),
        ),
        required=False,
    )
    sort_by = forms.ChoiceField(
        choices=(
            ("-created_at", "Date Created"),
            ("product__sku", "SKU"),
            ("product__product_range__name", "Name"),
            ("-closed_at", "Date Fulfilled"),
            ("fulfilled_by__first_name", "Fulfilled By"),
            ("status", "Status"),
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add supplier choices."""
        super().__init__(*args, **kwargs)
        cutoff_date = now() - dt.timedelta(days=360)
        supplier_ids = (
            models.FBAOrder.objects.filter(created_at__gte=cutoff_date)
            .values_list("product__supplier", flat=True)
            .distinct()
        )
        suppliers = Supplier.objects.filter(id__in=supplier_ids).order_by("name")
        self.fields["supplier"].choices = [("", "---------")] + [
            (supplier.id, supplier.name) for supplier in suppliers
        ]
        self.fields["country"].empty_label = "All"

    @staticmethod
    def clean_date(date, time):
        """Return date as a timezone aware datetime."""
        if date is None:
            return None
        return make_aware(datetime.combine(date, time))

    def clean_created_from(self):
        """Return a timezone aware datetime object from the submitted date."""
        return self.clean_date(
            self.cleaned_data.get("created_from"), datetime.min.time()
        )

    def clean_created_to(self):
        """Return a timezone aware datetime object from the submitted date."""
        return self.clean_date(self.cleaned_data.get("created_to"), datetime.max.time())

    def clean_fulfilled_from(self):
        """Return a timezone aware datetime object from the submitted date."""
        return self.clean_date(
            self.cleaned_data.get("fulfilled_from"), datetime.min.time()
        )

    def clean_fulfilled_to(self):
        """Return a timezone aware datetime object from the submitted date."""
        return self.clean_date(
            self.cleaned_data.get("fulfilled_to"), datetime.max.time()
        )

    def clean_prioritised(self):
        """Return the priorised filter value."""
        prioritised = self.cleaned_data["prioritised"]
        if prioritised == self.PRIORITISED:
            return True
        if prioritised == self.UNPRIORITISED:
            return False
        return None

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        kwargs = {
            "created_at__gte": data.get("created_from"),
            "created_at__lte": data.get("created_to"),
            "closed_at__gte": data.get("fulfilled_from"),
            "closed_at__lte": data.get("fulfilled_to"),
            "status": data.get("status"),
            "region__name": data.get("country"),
            "product__supplier": data.get("supplier"),
            "fulfilled_by": data.get("fulfilled_by"),
        }
        return {
            key: value
            for key, value in kwargs.items()
            if value is not None and value != ""
        }

    def get_queryset(self):
        """Return a queryset of orders based on the submitted data."""
        kwargs = self.query_kwargs(self.cleaned_data)
        qs = models.FBAOrder.objects.filter(**kwargs)
        if sort_by := self.cleaned_data.get("sort_by"):
            qs = qs.order_by(sort_by)
        else:
            qs = qs.order_by("-created_at")
        if search_text := self.cleaned_data.get("search"):
            qs = self.text_search(search_text, qs)
        if closed := self.cleaned_data.get("closed"):
            qs = qs.filter(closed_at__isnull=(closed == self.NOT_CLOSED))

        qs = self.filter_priority(qs)
        qs = (
            qs.select_related(
                "region__country",
            )
            .prefetch_related(
                "product",
                "product__supplier",
                "product__product_range",
                "tracking_numbers",
                "product__variation_option_values",
            )
            .distinct()
        )
        return qs

    def text_search(self, search_text, qs):
        """Filter the queryset based on search text."""
        qs = qs.filter(
            Q(
                Q(product__sku__icontains=search_text)
                | Q(product__product_range__name__icontains=search_text)
                | Q(tracking_numbers__tracking_number=search_text)
                | Q(product_asin__icontains=search_text)
            )
        )
        return qs

    def filter_priority(self, qs):
        """Return qs filtered by priority."""
        prioritised = self.cleaned_data.get("prioritised")
        if prioritised is True:
            return qs.prioritised()
        if prioritised is False:
            return qs.unprioritised()
        else:
            return qs


class FulfillFBAOrderForm(forms.ModelForm):
    """Form for fulfilling FBA orders."""

    def __init__(self, *args, **kwargs):
        """Set required fields."""
        super().__init__(*args, **kwargs)
        max_weight = self.instance.region.max_weight
        self.fields["box_weight"].label += " (kg)"
        self.fields["box_weight"].widget.attrs["max"] = max_weight
        self.fields["box_weight"].required = True
        self.fields["quantity_sent"].required = True
        self.fields["fulfilled_by"].required = True
        if self.instance.fulfilled_by is None:
            self.fields["fulfilled_by"].queryset = Staff.unhidden.filter(
                fba_packer=True
            )
        else:
            self.fields["fulfilled_by"].queryset = Staff.objects.filter(fba_packer=True)

    class Meta:
        """Meta class for FulfillFBAOrderForm."""

        model = models.FBAOrder
        fields = [
            "box_weight",
            "quantity_sent",
            "fulfilled_by",
            "update_stock_level_when_complete",
            "notes",
        ]


class OnHoldOrderFilter(forms.Form):
    """Form for filtering the FBA order list."""

    search = forms.CharField(required=False)
    created_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "datepicker", "size": "6"}),
    )
    created_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "datepicker", "size": "6"}),
    )
    country = forms.ModelChoiceField(models.FBARegion.objects.all(), required=False)
    supplier = forms.ChoiceField(choices=[], required=False)
    sort_by = forms.ChoiceField(
        choices=(
            ("created_at", "Date Created"),
            ("product__sku", "SKU"),
            ("product__product_range__sku", "Name"),
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add supplier choices."""
        super().__init__(*args, **kwargs)
        supplier_ids = (
            models.FBAOrder.objects.on_hold()
            .values_list("product__supplier", flat=True)
            .order_by("product__supplier")
            .distinct()
        )
        suppliers = Supplier.objects.filter(id__in=supplier_ids)
        self.fields["supplier"].choices = [("", "---------")] + [
            (supplier.id, supplier.name) for supplier in suppliers
        ]

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

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        kwargs = {
            "created_at__gte": data.get("created_from"),
            "created_at__lte": data.get("created_to"),
            "region__name": data.get("country"),
            "product__supplier": data.get("supplier"),
            "on_hold": True,
            "closed_at__isnull": True,
        }
        return {
            key: value
            for key, value in kwargs.items()
            if value is not None and value != ""
        }

    def get_queryset(self):
        """Return a queryset of orders based on the submitted data."""
        kwargs = self.query_kwargs(self.cleaned_data)
        qs = models.FBAOrder.objects.filter(**kwargs)
        if sort_by := self.cleaned_data["sort_by"]:
            qs = qs.order_by(sort_by)
        else:
            qs = qs.order_by("-created_at")
        if search_text := self.cleaned_data["search"]:
            qs = self.text_search(search_text, qs)
        qs = qs = qs.select_related(
            "region__country",
        ).prefetch_related(
            "product",
            "product__supplier",
            "product__product_range",
            "tracking_numbers",
            "product__variation_option_values",
        )
        return qs

    def text_search(self, search_text, qs):
        """Filter the queryset based on search text."""
        qs = qs.filter(
            Q(
                Q(product__sku__icontains=search_text)
                | Q(product__product_range__name__icontains=search_text)
                | Q(product_asin__icontains=search_text)
            )
        )
        return qs


class StoppedOrderFilter(forms.Form):
    """Form for filtering the FBA order list."""

    search = forms.CharField(required=False)
    stopped_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "datepicker", "size": "6"}),
    )
    stopped_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "datepicker", "size": "6"}),
    )
    country = forms.ModelChoiceField(models.FBARegion.objects.all(), required=False)
    supplier = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        """Add supplier choices."""
        super().__init__(*args, **kwargs)
        supplier_ids = (
            models.FBAOrder.objects.stopped()
            .values_list("product__supplier", flat=True)
            .order_by("product__supplier")
            .distinct()
        )
        suppliers = Supplier.objects.filter(id__in=supplier_ids)
        self.fields["supplier"].choices = [("", "---------")] + [
            (supplier.id, supplier.name) for supplier in suppliers
        ]

    def clean_stopped_from(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["stopped_from"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.min.time()))

    def clean_stopped_to(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["stopped_to"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.max.time()))

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        kwargs = {
            "stopped_at__gte": data.get("stopped_from"),
            "stopped_at__lte": data.get("stopped_to"),
            "region__name": data.get("country"),
            "product__supplier": data.get("supplier"),
            "closed_at__isnull": True,
        }
        return {
            key: value
            for key, value in kwargs.items()
            if value is not None and value != ""
        }

    def get_queryset(self):
        """Return a queryset of orders based on the submitted data."""
        kwargs = self.query_kwargs(self.cleaned_data)
        qs = models.FBAOrder.objects.stopped().filter(**kwargs)
        if search_text := self.cleaned_data["search"]:
            qs = self.text_search(search_text, qs)
        qs = qs = (
            qs.select_related(
                "region__country",
            )
            .prefetch_related(
                "product",
                "product__supplier",
                "product__product_range",
                "tracking_numbers",
                "product__variation_option_values",
            )
            .order_by("stopped_until")
        )
        return qs

    def text_search(self, search_text, qs):
        """Filter the queryset based on search text."""
        qs = qs.filter(
            Q(
                Q(product__sku__icontains=search_text)
                | Q(product__product_range__name__icontains=search_text)
                | Q(product_asin__icontains=search_text)
            )
        )
        return qs


class ShipmentDestinationForm(forms.ModelForm):
    """Model form for fba.models.FBAShipmentDestination."""

    class Meta:
        """Meta class for fba.forms.ShipmentDestinationForm."""

        model = models.FBAShipmentDestination
        exclude = ("is_enabled",)


class ShipmentOrderForm(forms.ModelForm):
    """Model form for fba.models.FBAShipmentOrder."""

    class Meta:
        """Meta class for fba.forms.ShipmentOrderForm."""

        model = models.FBAShipmentOrder
        exclude = ("is_on_hold", "export", "filing_error")

        widgets = {
            "planned_shipment_date": forms.DateInput(
                attrs={"class": "datepicker", "size": "6"}
            )
        }


class PackageForm(forms.ModelForm):
    """Model form for fba.models.FBAShipmentPackage."""

    class Meta:
        """Meta class for fba.forms.PackageForm."""

        model = models.FBAShipmentPackage
        exclude = ()

        widgets = {
            "shipment_order": forms.HiddenInput(),
        }


class ItemForm(forms.ModelForm):
    """Model form for fba.models.FBAShipmentItem."""

    def __init__(self, *args, **kwargs):
        """Set the value field to convert pence and pounds."""
        super().__init__(*args, **kwargs)
        self.fields["value"].widget = CurrencyWidget()
        self.fields["value"].to_python = lambda x: int(float(x) * 100)

    class Meta:
        """Meta class for fba.forms.PackageForm."""

        model = models.FBAShipmentItem
        exclude = ()
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


PackageFormset = forms.inlineformset_factory(
    models.FBAShipmentOrder,
    models.FBAShipmentPackage,
    form=PackageForm,
    extra=5,
)

ItemFormset = forms.inlineformset_factory(
    models.FBAShipmentPackage, models.FBAShipmentItem, form=ItemForm, extra=5
)


class SplitFBAOrderShipmentForm(forms.Form):
    """Form for splitting an FBA order into packages."""

    length_cm = forms.IntegerField()
    width_cm = forms.IntegerField()
    height_cm = forms.IntegerField()
    weight = forms.IntegerField()
    quantity = forms.IntegerField()
    value = forms.FloatField(initial=1.00)


SplitFBAOrderShipmentFormset = forms.formset_factory(
    form=SplitFBAOrderShipmentForm, extra=5
)


class TrackingNumbersForm(forms.ModelForm):
    """Form for updating FBA order tracking numbers."""

    tracking_numbers = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        """Meta class for TrackingNumbersForm."""

        model = models.FBAOrder
        fields = ["id"]

    def clean(self):
        """Clean form submission data."""
        cleaned_data = super().clean()
        cleaned_data["tracking_numbers"] = [
            _ for _ in json.loads(cleaned_data["tracking_numbers"]) if _
        ]
        return cleaned_data

    def save(self):
        """Update FBA Order tracking numbers."""
        models.FBATrackingNumber.objects.update_tracking_numbers(
            self.instance, *self.cleaned_data["tracking_numbers"]
        )
        if self.instance.tracking_numbers.count() > 0:
            self.instance.close()
        return super().save()


class FBAShipmentFilter(forms.Form):
    """Form for filtering the FBA order list."""

    search = forms.CharField(required=False)
    completed_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "datepicker", "size": "6"}),
    )
    completed_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"class": "datepicker", "size": "6"}),
    )
    destination = forms.ModelChoiceField(
        models.FBAShipmentDestination.objects.all(), required=False
    )
    user = forms.ModelChoiceField(
        get_user_model().objects.filter(fba_shipments__isnull=False).distinct(),
        required=False,
    )

    def clean_completed_from(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["completed_from"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.min.time()))

    def clean_completed_to(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["completed_to"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.max.time()))

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        kwargs = {
            "parcelhub_shipment__created_at__gte": data.get("completed_from"),
            "parcelhub_shipment__created_at__lte": data.get("completed_to"),
            "destination": data.get("destination"),
            "user": data.get("user"),
        }
        return {
            key: value
            for key, value in kwargs.items()
            if value is not None and value != ""
        }

    def get_queryset(self):
        """Return a queryset of orders based on the submitted data."""
        kwargs = self.query_kwargs(self.cleaned_data)
        qs = (
            models.FBAShipmentOrder.objects.filter(parcelhub_shipment__isnull=False)
            .filter(**kwargs)
            .order_by("-parcelhub_shipment__created_at")
        )
        if search_text := self.cleaned_data["search"]:
            qs = self.text_search(search_text, qs)
        qs = qs.prefetch_related(
            "parcelhub_shipment",
            "shipment_package",
            "shipment_package__shipment_item",
        )
        return qs.distinct()

    def text_search(self, search_text, qs):
        """Filter the queryset based on search text."""
        if search_text.startswith("STC_FBA_"):
            qs = qs.filter(id=int(search_text[8:]))
        else:
            qs = qs.filter(
                Q(
                    Q(shipment_package__shipment_item__sku__icontains=search_text)
                    | Q(
                        shipment_package__shipment_item__description__icontains=search_text
                    )
                )
            )
        return qs


class StopFBAOrderForm(forms.ModelForm):
    """Form for marking FBA Orders as stopped."""

    class Meta:
        """Meta class for StopFBAOrderForm."""

        model = models.FBAOrder
        fields = {"is_stopped", "stopped_at", "stopped_reason", "stopped_until"}
        widgets = {
            "is_stopped": forms.HiddenInput(),
            "stopped_at": forms.HiddenInput(),
            "stopped_until": forms.DateInput(
                attrs={"class": "datepicker", "size": "6"}
            ),
        }


class FBAShipmentDestinationForm(forms.Form):
    """Form for selecting shipment destinations."""

    class DestinationField(SelectizeModelChoiceField):
        """Field for selecting shipment destinations."""

        def get_queryset(self):
            """Return a queryset of shipment destinations."""
            return models.FBAShipmentDestination.objects.filter(is_enabled=True)

    destination = DestinationField()
