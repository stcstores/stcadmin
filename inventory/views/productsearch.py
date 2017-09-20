from django.shortcuts import render
from django.views.generic.edit import FormView
from inventory.forms import ProductSearchForm

from .views import InventoryUserMixin


class ProductSearch(InventoryUserMixin, FormView):
    template_name = 'inventory/product_search.html'
    form_class = ProductSearchForm

    def form_valid(self, form):
        return render(
            self.request, 'inventory/product_search.html', {
                'form': form,
                'product_ranges': form.ranges})
