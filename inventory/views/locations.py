from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

import cc_products
from inventory import models
from inventory.forms import LocationsFormSet

from .views import InventoryUserMixin


class LocationFormView(InventoryUserMixin, FormView):

    template_name = 'inventory/locations.html'
    form_class = LocationsFormSet

    def dispatch(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = cc_products.get_range(self.range_id)
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        product_ids = [p.id for p in self.product_range.products]
        kwargs['form_kwargs'] = [{'product_id': p} for p in product_ids]
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'inventory:locations', kwargs={'range_id': self.range_id})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['formset'] = context.pop('form')
        context['product_range'] = self.product_range
        context['warehouses'] = models.Warehouse.objects.all()
        return context

    def form_valid(self, forms):
        for form in forms:
            form.save()
        messages.add_message(
            self.request, messages.SUCCESS, 'Locations Updated')
        return super().form_valid(form)
