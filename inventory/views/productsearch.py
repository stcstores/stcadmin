"""Product Search page view."""

from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from inventory import forms
from inventory.models import Products

from .views import InventoryUserMixin


class InventorySearch(InventoryUserMixin, TemplateView):
    """View for searching the inventory with the search bar."""

    EXCLUDE = "exclude"
    INCLUDE = "include"
    EXCLUSIVE = "exclusive"

    template_name = "inventory/search/inventory_search.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        search_term = self.request.GET.get("search_text")
        end_of_line = self.request.GET.get("end_of_line")
        ranges = Products.get_ranges(search_term)
        if end_of_line == self.EXCLUDE:
            ranges = Products.filter_end_of_line(ranges)
        elif end_of_line == self.EXCLUSIVE:
            ranges = Products.filter_not_end_of_line(ranges)
        context["product_ranges"] = ranges
        return context


class AdvancedSearch(InventoryUserMixin, FormView):
    """View for product search page."""

    template_name = "inventory/search/advanced_search.html"
    form_class = forms.AdvancedInventorySearchForm

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        return render(
            self.request,
            "inventory/search/advanced_search.html",
            {"form": form, "product_ranges": form.cleaned_data["ranges"]},
        )
