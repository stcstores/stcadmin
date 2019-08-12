"""View for Product page."""

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from inventory import forms, models
from inventory.cloud_commerce_updater import ProductUpdater

from .views import InventoryUserMixin


class ProductView(InventoryUserMixin, FormView):
    """View for ProductForm."""

    template_name = "inventory/product.html"
    form_class = forms.ProductForm

    def dispatch(self, *args, **kwargs):
        """Process HTTP request."""
        product_ID = self.kwargs.get("product_id")
        self.product = get_object_or_404(models.Product, product_ID=product_ID)
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        """Return kwargs for form."""
        kwargs = super().get_form_kwargs()
        kwargs["product"] = self.product
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        form.save(updater_class=ProductUpdater)
        messages.add_message(self.request, messages.SUCCESS, "Product Updated")
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:product", kwargs={"product_id": self.product.product_ID}
        )

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["product"] = self.product
        context_data["product_range"] = self.product.product_range
        return context_data
