"""View for updating Product Warehouse Bays."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import FormView

from inventory import models
from inventory.forms import LocationsFormSet

from .views import InventoryUserMixin


class LocationFormView(InventoryUserMixin, FormView):
    """View for LocationsFormSet."""

    template_name = "inventory/product_range/locations.html"
    form_class = LocationsFormSet

    def get_initial(self):
        """Return initial form values."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        self.products = self.product_range.products.variations()
        initial = []
        for product in self.products:
            bays = [
                bay_link.bay.id
                for bay_link in models.ProductBayLink.objects.filter(product=product)
            ]
            initial.append({"product_id": product.id, "bays": bays})
        return initial

    def form_valid(self, formset):
        """Update product bays."""
        for form in formset:
            form.save(user=self.request.user)
        messages.add_message(self.request, messages.SUCCESS, "Locations Updated")
        return redirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = self.product_range
        context["formset"] = context["form"]
        for i, form in enumerate(context["formset"]):
            form.product = self.products[i]
        return context

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return self.product_range.get_absolute_url()
