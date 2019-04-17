"""DescriptionsView class."""

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from inventory import forms, models
from inventory.cloud_commerce_updater import RangeUpdater

from .views import InventoryUserMixin


class DescriptionsView(InventoryUserMixin, FormView):
    """View for DescriptionForm."""

    form_class = forms.DescriptionForm
    template_name = "inventory/product_range/descriptions.html"

    def dispatch(self, *args, **kwargs):
        """Process HTTP request."""
        self.range_id = self.kwargs.get("range_id")
        self.product_range = get_object_or_404(
            models.ProductRange, range_ID=self.range_id
        )
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        """Get initial data for form."""
        initial = super().get_initial()
        initial["title"] = self.product_range.name
        initial["department"] = self.product_range.department
        initial["description"] = self.product_range.description
        initial["amazon_bullets"] = self.product_range.amazon_bullet_points.split("|")
        initial["search_terms"] = self.product_range.amazon_search_terms.split("|")
        return initial

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        updater = RangeUpdater(self.product_range)
        updater.set_name(form.cleaned_data["title"])
        updater.set_description(form.cleaned_data["description"])
        updater.set_amazon_bullet_points("|".join(form.cleaned_data["amazon_bullets"]))
        updater.set_amazon_search_terms("|".join(form.cleaned_data["search_terms"]))
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
