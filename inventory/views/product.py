"""View for Product page."""

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView

from inventory import forms, models

from .views import InventoryUserMixin


class ProductView(InventoryUserMixin, UpdateView):
    """View for ProductForm."""

    template_name = "inventory/product.html"
    model = models.Product
    form_class = forms.EditProductForm

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        messages.add_message(self.request, messages.SUCCESS, "Product Updated")
        return reverse_lazy("inventory:product", kwargs={"pk": self.object.pk})

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context_data = super().get_context_data(*args, **kwargs)
        form = context_data["form"]
        context_data["product"] = form.instance
        context_data["product_range"] = form.instance.product_range
        return context_data
