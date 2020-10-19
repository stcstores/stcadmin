"""Forms for the FBA app."""

from datetime import datetime

from ccapi import CCAPI
from django import forms
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
                self.add_error("Too many products found")
            else:
                product = search_result[0]
            cleaned_data["product_ID"] = product.variation_id
        except Exception:
            self.add_error("Product not found")


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
        self.fields["product_SKU"].disabled = True
        self.fields["product_ID"].disabled = True
        self.fields["product_name"].disabled = True
        self.fields["selling_price"].widget = CurrencyWidget()
        self.fields["selling_price"].to_python = lambda x: int(float(x) * 100)
        self.fields["region"].widget = forms.HiddenInput()
        self.fields["region"].required = False
        self.fields["country"] = forms.ModelChoiceField(
            queryset=models.FBACountry.objects.all()
        )

    class Meta:
        """Meta class for CreateFBAOrderForm."""

        model = models.FBAOrder
        fields = [
            "product_ID",
            "product_SKU",
            "product_name",
            "region",
            "selling_price",
            "FBA_fee",
            "aproximate_quantity",
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

    status = forms.ChoiceField(
        choices=(
            ("", ""),
            (models.FBAOrder.NOT_PROCESSED, models.FBAOrder.NOT_PROCESSED),
            (models.FBAOrder.AWAITING_BOOKING, models.FBAOrder.AWAITING_BOOKING),
            (models.FBAOrder.FULFILLED, models.FBAOrder.FULFILLED),
        ),
        required=False,
    )
    created_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    created_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    fulfilled_from = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    fulfilled_to = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": "datepicker"})
    )
    country = forms.ModelChoiceField(models.FBARegion.objects.all(), required=False)
    sort_by = forms.ChoiceField(
        choices=(
            ("", ""),
            ("product_SKU", "SKU"),
            ("product_name", "Name"),
            ("created_at", "Date Created"),
            ("closed_at", "Date Fulfilled"),
            ("fullfilled_by__first_name", "Fulfilled By"),
            ("status", "Status"),
        ),
        required=False,
    )

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
            print(f"Sort by: {sort_by}")
            qs = qs.order_by(sort_by)
        return qs


class FulfillFBAOrderForm(forms.ModelForm):
    """Form for fullfilling FBA orders."""

    def __init__(self, *args, **kwargs):
        """Set required fields."""
        super().__init__(*args, **kwargs)
        dimension_unit = self.instance.region.dimension_unit
        max_weight = self.instance.region.max_weight
        max_size = self.instance.region.max_size
        for field in ("box_width", "box_height", "box_depth"):
            self.fields[field].label += f" ({dimension_unit})"
            self.fields[field].widget.attrs["max"] = max_size
        self.fields["box_weight"].label += " (kg)"
        self.fields["box_weight"].widget.attrs["max"] = max_weight
        self.fields["box_weight"].required = True
        self.fields["box_width"].required = True
        self.fields["box_height"].required = True
        self.fields["box_depth"].required = True
        self.fields["quantity_sent"].required = True

    class Meta:
        """Meta class for FulfillFBAOrderForm."""

        model = models.FBAOrder
        fields = [
            "box_weight",
            "box_width",
            "box_height",
            "box_depth",
            "quantity_sent",
            "notes",
        ]
