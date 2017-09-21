from ccapi import CCAPI
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from inventory import forms

from .views import InventoryUserMixin


class Product(InventoryUserMixin, FormView):
    template_name = 'inventory/product.html'
    form_class = forms.ProductForm

    def dispatch(self, *args, **kwargs):
        self.product_id = self.kwargs.get('product_id')
        self.product = CCAPI.get_product(self.product_id)
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['stock_level'] = self.product.stock_level
        initial['weight'] = self.product.weight
        initial['height'] = self.product.height_cm
        initial['length'] = self.product.length_cm
        initial['width'] = self.product.width_cm
        return initial

    def form_valid(self, form):
        #  Update Product
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'inventory:product', kwargs={'product_id': self.product_id})

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['product'] = self.product
        return context_data
