"""Product Search page view."""

from django.shortcuts import render
from django.views.generic.edit import FormView

from inventory.forms import ProductSearchForm

from .views import InventoryUserMixin


class ProductSearchView(InventoryUserMixin, FormView):
    """View for product search page."""

    template_name = 'inventory/product_search.html'
    form_class = ProductSearchForm

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        return render(
            self.request, 'inventory/product_search.html', {
                'form': form,
                'product_ranges': form.ranges})
