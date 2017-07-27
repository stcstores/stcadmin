from django.shortcuts import render
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from inventory.forms import RangeSearchForm


class RangeSearch(LoginRequiredMixin, FormView):
    template_name = 'inventory/range_search.html'
    form_class = RangeSearchForm

    def form_valid(self, form):
        return render(
            self.request, 'inventory/range_search.html', {
                'form': form,
                'product_ranges': form.ranges})
