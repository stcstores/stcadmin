"""View for updating Product Warehouse Bays."""

import cc_products
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

from inventory.forms import LocationsFormSet
from product_editor.editor_manager import ProductEditorBase

from .views import InventoryUserMixin


class LocationFormView(InventoryUserMixin, TemplateView):
    """View for LocationsFormSet."""

    template_name = "inventory/locations.html"
    DEPARTMENT = ProductEditorBase.DEPARTMENT
    WAREHOUSE = ProductEditorBase.WAREHOUSE
    BAYS = ProductEditorBase.BAYS

    def get(self, *args, **kwargs):
        """Process GET HTTP request."""
        self.range_id = self.kwargs.get("range_id")
        self.product_range = cc_products.get_range(self.range_id)
        self.formset = LocationsFormSet(
            form_kwargs=[{"product": p} for p in self.product_range.products]
        )
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Process POST HTTP request."""
        self.range_id = self.kwargs.get("range_id")
        self.product_range = cc_products.get_range(self.range_id)
        self.formset = LocationsFormSet(
            self.request.POST,
            form_kwargs=[{"product": p} for p in self.product_range.products],
        )
        if self.formset.is_valid():
            for form in self.formset:
                form.save()
            messages.add_message(self.request, messages.SUCCESS, "Locations Updated")
            return redirect(self.get_success_url())
        return super().get(*args, **kwargs)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy("inventory:locations", kwargs={"range_id": self.range_id})

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = self.product_range
        context["formset"] = self.formset
        return context
