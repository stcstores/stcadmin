"""View for setting the order of products in a range."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

from inventory import models
from inventory.cloud_commerce_updater import ProductUpdater
from inventory.forms import VariationsFormSet

from .views import InventoryUserMixin


class VariationsView(InventoryUserMixin, TemplateView):
    """View for setting the order of products in a range."""

    template_name = "inventory/product_range/variations.html"

    def dispatch(self, *args, **kwargs):
        """Load the formset."""
        self.range_id = self.kwargs.get("range_id")
        self.product_range = get_object_or_404(
            models.ProductRange, range_ID=self.range_id
        )
        self.formset = VariationsFormSet(
            self.request.POST or None,
            form_kwargs=[{"product": p} for p in self.product_range.products()],
        )
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Process POST HTTP request."""
        if self.formset.is_valid():
            for form in self.formset:
                form.save(updater_class=ProductUpdater)
            messages.add_message(
                self.request, messages.SUCCESS, "Variation Order Updated"
            )
            return redirect(self.get_success_url())
        else:
            return super().get(*args, **kwargs)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy("inventory:variations", kwargs={"range_id": self.range_id})

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = self.product_range
        context["formset"] = self.formset
        context["variations"] = self.product_range.variation_values()
        return context
