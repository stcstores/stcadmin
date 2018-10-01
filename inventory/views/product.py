"""View for Product page."""

import cc_products
from ccapi import CCAPI
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from inventory import forms, models

from .views import InventoryUserMixin


class ProductView(InventoryUserMixin, FormView):
    """View for ProductForm."""

    template_name = "inventory/product.html"
    form_class = forms.ProductForm

    def dispatch(self, *args, **kwargs):
        """Process HTTP request."""
        self.product_id = self.kwargs.get("product_id")
        self.product = cc_products.get_product(self.product_id)
        self.product_range = self.product.product_range
        self.option_names = [
            o.name for o in self.product_range.options.selected_options
        ]
        self.option_data = CCAPI.get_product_options()
        self.options = {
            option.option_name: [value.value for value in option]
            for option in self.option_data
            if option.option_name in self.option_names
        }
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        """Return kwargs for form."""
        kwargs = super().get_form_kwargs()
        kwargs["product"] = self.product
        kwargs["product_range"] = self.product_range
        kwargs["options"] = self.options
        return kwargs

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        form.save()
        messages.add_message(self.request, messages.SUCCESS, "Product Updated")
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy("inventory:product", kwargs={"product_id": self.product_id})

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["product"] = self.product
        context_data["product_range"] = self.product.product_range
        if "Linn Title" in self.option_names:
            context_data["linnworks_title"] = self.product.linn_title
        if "Linn SKU" in self.option_names:
            context_data["linnworks_sku"] = self.product.linn_sku
        department = self.product.department
        try:
            warehouse = models.Warehouse.objects.get(name=department)
        except models.Warehouse.DoesNotExist:
            context_data["warehouse_bays"] = []
        else:
            context_data["warehouse_bays"] = warehouse.bay_set.all()
        return context_data
