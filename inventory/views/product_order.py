"""View for setting the order of products in a range."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView

from inventory import models
from inventory.forms import ProductOrderFormSet

from .views import InventoryUserMixin


class ProductOrderView(InventoryUserMixin, TemplateView):
    """View for setting the order of products in a range."""

    template_name = "inventory/product_range/product_order.html"

    def dispatch(self, *args, **kwargs):
        """Load the formset."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        self.formset = ProductOrderFormSet(
            self.request.POST or None,
            form_kwargs=[
                {"product": p}
                for p in self.product_range.products.variations()
                .active()
                .filter(is_end_of_line=False)
            ],
        )
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Process POST HTTP request."""
        if self.formset.is_valid():
            for form in self.formset:
                form.save()
            messages.add_message(
                self.request, messages.SUCCESS, "Variation Order Updated"
            )
            return redirect(self.get_success_url())
        else:
            return super().get(*args, **kwargs)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:product_order", kwargs={"range_pk": self.product_range.pk}
        )

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = self.product_range
        context["formset"] = self.formset
        return context
