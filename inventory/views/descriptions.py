from ccapi import CCAPI
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from inventory import forms

from .views import InventoryUserMixin


class Descriptions(InventoryUserMixin, FormView):
    form_class = forms.DescriptionForm
    template_name = 'inventory/descriptions.html'

    def dispatch(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = CCAPI.get_range(self.range_id)
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        first_product = CCAPI.get_product(self.product_range.products[0].id)
        initial['title'] = self.product_range.name
        initial['description'] = first_product.description
        return initial

    def form_valid(self, form):
        self.product_range.set_description(
            form.cleaned_data['description'], update_channels=True)
        name = form.cleaned_data['title']
        self.product_range.set_name(name)
        product_ids = [p.id for p in self.product_range.products]
        CCAPI.set_product_name(name, product_ids)
        CCAPI.update_product_on_sales_channel(
            range_id=self.product_range.id, product_ids=product_ids,
            request_type='name', value_1=name,
            channels=self.product_range.get_sales_channel_ids())
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'inventory:descriptions', kwargs={'range_id': self.range_id})

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['product_range'] = self.product_range
        return context_data
