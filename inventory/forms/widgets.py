"""Widgets for custom or combined fields."""

import json

from django import forms
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django_select2.forms import ModelSelect2Widget

from inventory import models

from .base import ProductEditorBase


class ModelSelect2CreateableWidget(ModelSelect2Widget):
    """Widget for selecting model instances with select2 and a create button."""

    template_name = "inventory/widgets/model_select_2_creatable_widget.html"
    create_new_url = ""

    def get_context(self, *args, **kwargs):
        """Add the URL to use to create the new instance to the context."""
        context = super(ModelSelect2Widget, self).get_context(*args, **kwargs)
        context["create_new_url"] = self.create_new_url
        return context


class BrandWidget(ModelSelect2CreateableWidget):
    """Widget for selecting or creating brands."""

    name = "brand"
    create_new_url = reverse_lazy("inventory:new_brand")
    model = models.Brand
    search_fields = ["name__icontains"]


class ManufacturerWidget(ModelSelect2CreateableWidget):
    """Widget for selecting or creating manufacturers."""

    name = "manufacturer"
    create_new_url = reverse_lazy("inventory:new_manufacturer")
    model = models.Manufacturer
    search_fields = ["name__icontains"]


class SupplierWidget(ModelSelect2CreateableWidget):
    """Widget for selecting or creating suppliers."""

    name = "supplier"
    create_new_url = reverse_lazy("inventory:new_supplier")
    model = models.Supplier
    search_fields = ["name__icontains"]


class HorizontalRadio(forms.RadioSelect):
    """Widget for radio buttons layed out horizontally."""

    template_name = "inventory/widgets/horizontal_radio.html"


class BaseSelectizeWidget:
    """Base class for widgets using selectize.js."""

    template_name = "inventory/widgets/selectize.html"


class HSCodeWidget(forms.TextInput):
    """Widget for HS Codes with search."""

    template_name = "product_editor/widgets/hs_code.html"


class MultipleSelectizeWidget(BaseSelectizeWidget, forms.SelectMultiple):
    """Widget for selectize fields allowing multiple values."""

    template_name = "inventory/widgets/selectize.html"

    def __init__(self, *args, **kwargs):
        """Set selectize options."""
        self.selectize_options = kwargs.pop("selectize_options")
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context(*args, **kwargs)
        context["widget"]["selectize_options"] = mark_safe(
            json.dumps(self.selectize_options)
        )
        return context


class SingleSelectizeWidget(BaseSelectizeWidget, forms.Select):
    """Widget for selectize fields allowing a single value."""

    def __init__(self, *args, **kwargs):
        """Set selectize options."""
        self.selectize_options = kwargs.pop("selectize_options", {})
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context(*args, **kwargs)
        context["widget"]["selectize_options"] = mark_safe(
            json.dumps(self.selectize_options)
        )
        return context


class SelectizeModelMultipleChoiceWidget(BaseSelectizeWidget, forms.SelectMultiple):
    """Widget for selecting multiple model objects."""

    selectize_options = {
        "delimiter": ",",
        "persist": False,
        "maxItems": None,
        "sortField": "text",
    }

    def get_context(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context(*args, **kwargs)
        context["widget"]["selectize_options"] = mark_safe(
            json.dumps(self.selectize_options)
        )
        return context


class VATPriceWidget(forms.MultiWidget):
    """Widget for VATPrice field."""

    template_name = "inventory/widgets/vat_price.html"
    required = True

    VAT_RATE = ProductEditorBase.VAT_RATE
    EX_VAT = ProductEditorBase.EX_VAT
    WITH_VAT_PRICE = "with_vat_price"

    def __init__(self, attrs=None):
        """Configure sub widgets."""
        if attrs is None:
            price_attrs = {}
        else:
            price_attrs = attrs.copy()
        price_attrs["min"] = 0
        price_attrs["step"] = 0.01
        widgets = [
            forms.Select(choices=self.vat_choices(), attrs=attrs),
            forms.NumberInput(attrs=price_attrs),
            forms.NumberInput(attrs=price_attrs),
        ]
        super().__init__(widgets, attrs)

    @staticmethod
    def vat_choices():
        """Return choices."""
        return (("", ""), (20, "20%"), (5, "5%"), (0, "Exempt"))

    def decompress(self, value):
        """Return value as a list of values."""
        if value:
            return [value[self.VAT_RATE], value[self.EX_VAT], ""]
        else:
            return ["", "", ""]


class DimensionsWidget(forms.MultiWidget):
    """Widget for Dimensions field."""

    template_name = "inventory/widgets/dimensions.html"
    required = False
    is_required = False

    def __init__(self, *args, **kwargs):
        """Configure sub widgets."""
        attrs = kwargs.get("attrs", None)
        widgets = [
            forms.NumberInput(attrs=attrs),
            forms.NumberInput(attrs=attrs),
            forms.NumberInput(attrs=attrs),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """Return value as a list of values."""
        if value:
            return [value["height"], value["length"], value["width"]]
        else:
            return ["", "", ""]
