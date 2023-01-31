"""View for Product Range page."""

from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateView

from inventory import models
from linnworks.models.stock_manager import StockManager

from .views import InventoryUserMixin


class ProductRangeView(InventoryUserMixin, TemplateView):
    """Product Range page view."""

    template_name = "inventory/product_range/product_range.html"

    def get(self, *args, **kwargs):
        """Process HTTP request."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        return super().get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["product_range"] = self.product_range
        products = self.product_range.products.variations()
        context_data["products"] = products
        if not self.product_range.is_end_of_line:
            product_skus = products.filter(is_end_of_line=False).values_list(
                "sku", flat=True
            )
            try:
                context_data["products_exist"] = StockManager.products_exist(
                    *product_skus
                )
            except Exception:
                context_data["products_exist"] = None
        else:
            context_data["products_exist"] = None
        return context_data


class ChannelLinks(InventoryUserMixin, TemplateView):
    """View for showing listing linked to products."""

    template_name = "inventory/product_range/channel_links.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs["range_pk"]
        )
        products = product_range.products.variations()
        skus = [product.sku for product in products]
        channel_links = StockManager.channel_links(*skus)
        for product in products:
            product.channel_links = channel_links.get(product.sku, [])
        context["product_range"] = product_range
        context["products"] = products
        return context
