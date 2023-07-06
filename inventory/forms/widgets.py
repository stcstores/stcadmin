"""Widgets for custom or combined fields."""

import json

from django import forms
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget

from inventory import models


class SingleBayWidget(ModelSelect2Widget):
    """Widget for selecting a bay."""

    model = models.Bay
    search_fields = ["name__icontains"]


class MultipleBayWidget(ModelSelect2MultipleWidget):
    """Widget for selecting a bay."""

    model = models.Bay
    search_fields = ["name__icontains"]


class AdditionalSuppliersWidget(ModelSelect2MultipleWidget):
    """Widget for selecting additional_suppliers."""

    queryset = models.Supplier.objects.filter(active=True)
    search_fields = ["name__icontains"]


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
