from ccapi import CCAPI
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from inventory import forms

from .views import InventoryUserMixin


class ProductRange(InventoryUserMixin, FormView):
    template_name = 'inventory/product_range.html'
    form_class = forms.ProductRangeForm

    def dispatch(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = CCAPI.get_range(self.range_id)
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['end_of_line'] = self.product_range.end_of_line
        return initial

    def form_valid(self, form):
        if form.cleaned_data['end_of_line'] != self.product_range.end_of_line:
            self.product_range.set_end_of_line(
                form.cleaned_data['end_of_line'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'inventory:product_range', kwargs={'range_id': self.range_id})

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['product_range'] = self.product_range
        return context_data
