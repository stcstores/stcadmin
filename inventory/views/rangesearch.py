from django.shortcuts import render
from django.views.generic.edit import FormView
from inventory.forms import RangeSearchForm

from .views import InventoryUserMixin


class RangeSearch(InventoryUserMixin, FormView):
    template_name = 'inventory/range_search.html'
    form_class = RangeSearchForm

    def form_valid(self, form):
        return render(
            self.request, 'inventory/range_search.html', {
                'form': form,
                'product_ranges': form.ranges})
