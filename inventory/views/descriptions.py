"""DescriptionsView class."""

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from inventory import forms, models

from .views import InventoryUserMixin


class DescriptionsView(InventoryUserMixin, FormView):
    """View for CreateRangeForm."""

    form_class = forms.CreateRangeForm
    template_name = "inventory/product_range/descriptions.html"

    def dispatch(self, *args, **kwargs):
        """Process HTTP request."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        """Get initial data for form."""
        initial = super().get_initial()
        initial["title"] = self.product_range.name
        initial["description"] = self.product_range.description
        initial["amazon_bullets"] = self.product_range.amazon_bullet_points.split("|")
        initial["search_terms"] = self.product_range.amazon_search_terms.split("|")
        return initial

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        messages.add_message(self.request, messages.SUCCESS, "Description Updated")
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:descriptions", kwargs={"range_id": self.range_id}
        )

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context_data = super().get_context_data(*args, **kwargs)
        context_data["product_range"] = self.product_range
        return context_data
