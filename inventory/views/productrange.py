"""View for Product Range page."""

from ccapi import CCAPI
from django.views.generic.base import TemplateView

from .views import InventoryUserMixin


class ProductRangeView(InventoryUserMixin, TemplateView):
    """Product Range page view."""

    template_name = "inventory/product_range.html"

    def get(self, *args, **kwargs):
        """Process HTTP request."""
        self.get_range()
        if self.product_range is None or self.product_range.id == 0:
            return self.range_error()
        return super().get(*args, **kwargs)

    def get_range(self):
        """Get product range details from Cloud Commerce."""
        self.range_id = self.kwargs.get("range_id")
        try:
            self.product_range = CCAPI.get_range(self.range_id)
        except Exception:
            self.product_range = None

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["product_range"] = self.product_range
        return context_data

    def range_error(self):
        """Show error page."""
        return RangeError.as_view()(self.request)


class RangeError(TemplateView):
    """View for Product Range not found error page."""

    template_name = "inventory/product_range_404.html"

    def get(self, request, *args, **kwargs):
        """Return rendered response with 404 error code."""
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=404)
