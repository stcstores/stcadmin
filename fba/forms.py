"""Forms for the FBA app."""

from datetime import datetime

from ccapi import CCAPI
from django import forms
from django.db.models import Q
from django.utils.timezone import make_aware

from fba import models


class SelectFBAOrderProduct(forms.Form):
    """Form for selecting a product for an FBA order."""

    product_SKU = forms.CharField()

    def clean(self):
        """Add product ID to cleaned data."""
        cleaned_data = super().clean()
        try:
            search_result = CCAPI.search_products(cleaned_data["product_SKU"])
            if len(search_result) > 1:
                self.add_error("product_SKU", "Too many products found")
                return
            else:
                product = search_result[0]
            cleaned_data["product_ID"] = product.variation_id
        except Exception:
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


class CreateFBAOrderForm(forms.ModelForm):
    """Form for creating FBA orders."""

    def __init__(self, *args, **kwargs):
        """Disable non-editable fields."""
        super().__init__(*args, **kwargs)
        self.fields["product_SKU"].widget = forms.HiddenInput()
        self.fields["product_ID"].widget = forms.HiddenInput()
        self.fields["product_name"].widget = forms.HiddenInput()
        self.fields["product_weight"].widget = forms.HiddenInput()
        self.fields["product_hs_code"].widget = forms.HiddenInput()
        self.fields["product_image_url"].widget = forms.HiddenInput()
        self.fields["product_supplier"].widget = forms.HiddenInput()
        self.fields["product_purchase_price"].widget = forms.HiddenInput()
        self.fields["product_is_multipack"].widget = forms.HiddenInput()
        self.fields["selling_price"].widget = CurrencyWidget()
        self.fields["selling_price"].to_python = lambda x: int(float(x) * 100)
        self.fields["FBA_fee"].widget = CurrencyWidget()
        self.fields["FBA_fee"].to_python = lambda x: int(float(x) * 100)
        self.fields["region"].widget = forms.HiddenInput()
        self.fields["region"].required = False
        self.fields["country"] = forms.ModelChoiceField(
            queryset=models.FBACountry.objects.all()
        )
        field_order = [
            "product_ID",
            "product_SKU",
            "product_name",
            "product_weight",
            "product_hs_code",
            "product_image_url",
            "product_supplier",
            "product_purchase_price",
            "product_is_multipack",
            "region",
            "country",
            "product_asin",
            "selling_price",
            "FBA_fee",
            "aproximate_quantity",
            "small_and_light",
            "tracking_number",
            "is_combinable",
            "on_hold",
            "is_fragile",
            "notes",
        ] + self.__class__.Meta.fields
        new_fields = {key: self.fields[key] for key in field_order}
        self.fields = new_fields
        if self.instance.id is not None:
            self.initial["country"] = self.instance.region.default_country
        else:
            self.fields["tracking_number"].widget = forms.HiddenInput()

    class Meta:
        """Meta class for CreateFBAOrderForm."""

        model = models.FBAOrder
        fields = [
            "product_ID",
            "product_SKU",
            "product_name",
            "product_weight",
            "product_hs_code",
            "product_image_url",
            "product_supplier",
            "product_purchase_price",
            "product_asin",
            "product_is_multipack",
            "region",
            "selling_price",
            "FBA_fee",
            "aproximate_quantity",
            "small_and_light",
            "tracking_number",
            "is_combinable",
            "is_fragile",
            "on_hold",
            "notes",
        ]
        widgets = {"product_ID": forms.HiddenInput()}

    def clean(self):
        """Add region to cleaned data."""
        cleaned_data = super().clean()
        country = cleaned_data["country"]
        cleaned_data["region"] = country.region
        return cleaned_data


class FBAOrderFilter(forms.Form):
    """Form for filtering the FBA order list."""

    CLOSED = "closed"
    NOT_CLOSED = "not_closed"

    search = forms.CharField(required=False)
    status = forms.ChoiceField(
        choices=(
            ("", ""),
            (models.FBAOrder.NOT_PROCESSED, models.FBAOrder.NOT_PROCESSED),
            (models.FBAOrder.PRINTED, models.FBAOrder.PRINTED),
            (models.FBAOrder.AWAITING_BOOKING, models.FBAOrder.AWAITING_BOOKING),
            (models.FBAOrder.FULFILLED, models.FBAOrder.FULFILLED),
            (models.FBAOrder.ON_HOLD, models.FBAOrder.ON_HOLD),
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
    country = forms.ModelChoiceField(models.FBARegion.objects.all(), required=False)
    supplier = forms.ChoiceField(choices=[], required=False)
    closed = forms.ChoiceField(
        choices=(("", ""), (CLOSED, "Closed"), (NOT_CLOSED, "Not Closed")),
        required=False,
    )
    sort_by = forms.ChoiceField(
        choices=(
            ("-created_at", "Date Created"),
            ("product_SKU", "SKU"),
            ("product_name", "Name"),
            ("-closed_at", "Date Fulfilled"),
            ("fulfilled_by__first_name", "Fulfilled By"),
            ("status", "Status"),
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add supplier choices."""
        super().__init__(*args, **kwargs)
        self.fields["supplier"].choices = [
            (name, name)
            for name in models.FBAOrder.objects.values_list(
                "product_supplier", flat=True
            )
            .order_by("product_supplier")
            .distinct()
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

    def clean_fulfilled_from(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["fulfilled_from"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.min.time()))

    def clean_fulfilled_to(self):
        """Return a timezone aware datetime object from the submitted date."""
        date = self.cleaned_data["fulfilled_to"]
        if date is not None:
            return make_aware(datetime.combine(date, datetime.max.time()))

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        kwargs = {
            "created_at__gte": data.get("created_from"),
            "created_at__lte": data.get("created_to"),
            "closed_at__gte": data.get("fulfilled_from"),
            "closed_at__lte": data.get("fulfilled_to"),
            "status": data.get("status"),
            "region__name": data.get("country"),
            "product_supplier": data.get("supplier"),
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
        if closed := self.cleaned_data.get("closed"):
            qs = qs.filter(closed_at__isnull=(closed == self.NOT_CLOSED))
        qs = qs.select_related("region__default_country__country")
        return qs

    def text_search(self, search_text, qs):
        """Filter the queryset based on search text."""
        qs = qs.filter(
            Q(
                Q(product_SKU__icontains=search_text)
                | Q(product_name__icontains=search_text)
                | Q(tracking_number__icontains=search_text)
                | Q(product_asin__icontains=search_text)
            )
        )
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


class ShippingPriceForm(forms.ModelForm):
    """Form for setting corrected shipping prices."""

    def __init__(self, *args, **kwargs):
        """Set fields."""
        self.fba_order = kwargs.pop("fba_order")
        super().__init__(*args, **kwargs)
        self.fields["price_per_item"].widget = CurrencyWidget()
        self.fields["price_per_item"].to_python = lambda x: int(float(x) * 100)
        self.fields["shipping_price"] = forms.DecimalField(
            max_digits=7, decimal_places=2
        )
        self.fields["product_SKU"].widget = forms.HiddenInput()
        self.initial["product_SKU"] = self.fba_order.product_SKU
        self.fields = {key: value for key, value in reversed(list(self.fields.items()))}

    class Meta:
        """Meta class for ShippingPriceForm."""

        model = models.FBAShippingPrice
        fields = ["price_per_item", "product_SKU"]


class OnHoldOrderFilter(forms.Form):
    """Form for filtering the FBA order list."""

    CLOSED = "closed"
    NOT_CLOSED = "not_closed"

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
    closed = forms.ChoiceField(
        choices=(("", ""), (CLOSED, "Closed"), (NOT_CLOSED, "Not Closed")),
        required=False,
    )
    sort_by = forms.ChoiceField(
        choices=(
            ("created_at", "Date Created"),
            ("product_SKU", "SKU"),
            ("product_name", "Name"),
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Add supplier choices."""
        super().__init__(*args, **kwargs)
        self.fields["supplier"].choices = [("", "")] + [
            (name, name)
            for name in models.FBAOrder.objects.filter(
                on_hold=True, closed_at__isnull=True
            )
            .values_list("product_supplier", flat=True)
            .order_by("product_supplier")
            .distinct()
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
            "product_supplier": data.get("supplier"),
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
        if closed := self.cleaned_data.get("closed"):
            qs = qs.filter(closed_at__isnull=(closed == self.NOT_CLOSED))
        qs = qs.select_related("region__default_country__country")
        return qs

    def text_search(self, search_text, qs):
        """Filter the queryset based on search text."""
        qs = qs.filter(
            Q(
                Q(product_SKU__icontains=search_text)
                | Q(product_asin__icontains=search_text)
                | Q(product_name__icontains=search_text)
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
        exclude = ("is_on_hold", "export")


class PackageForm(forms.ModelForm):
    """Model form for fba.models.FBAShipmentPackage."""

    class Meta:
        """Meta class for fba.forms.PackageForm."""

        model = models.FBAShipmentPackage
        exclude = ()

        widgets = {
            "fba_order": forms.HiddenInput(),
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
