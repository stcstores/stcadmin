"""Views for handeling Product Images."""

from collections import defaultdict

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from inventory import models
from inventory.forms import ImagesForm

from .views import InventoryUserMixin


class ImageFormView(InventoryUserMixin, FormView):
    """View for ImagesForm."""

    template_name = "inventory/product_range/images.html"
    form_class = ImagesForm

    def get_products(self):
        """Retrive product details from Cloud Commerce."""
        self.range_id = self.kwargs.get("range_id")
        self.product_range = get_object_or_404(
            models.ProductRange, range_ID=self.range_id
        )
        self.products = self.product_range.products.variations()

    def get_options(self):
        """Return variation data for the products."""
        options = defaultdict(lambda: defaultdict(list))
        for product in self.products:
            for option, value in product.variation().items():
                options[option][value].append(product.product_ID)
        options = dict(options)
        for option, value in options.items():
            options[option] = dict(value)
        return options

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = self.product_range
        context["products"] = {
            product: models.ProductImage.objects.filter(product=product)
            for product in self.products
        }
        context["options"] = self.get_options()
        return context

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy("inventory:images", kwargs={"range_id": self.range_id})
