import cc_products
from ccapi import CCAPI
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from inventory import forms, models

from .views import InventoryUserMixin


class ProductView(InventoryUserMixin, FormView):
    template_name = 'inventory/product.html'
    form_class = forms.ProductForm

    def dispatch(self, *args, **kwargs):
        self.product_id = self.kwargs.get('product_id')
        self.product = cc_products.get_product(self.product_id)
        self.product_range = self.product.product_range
        self.option_names = [
            o.name for o in self.product_range.options.selected_options]
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = self.product
        kwargs['product_range'] = self.product_range
        kwargs['option_names'] = self.option_names
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['vat_rate'] = self.product.vat_rate
        initial['price'] = self.product.price
        initial['locations'] = self.product.bays
        initial['weight'] = self.product.weight
        initial['height'] = self.product.height
        initial['length'] = self.product.length
        initial['width'] = self.product.width
        initial['purchase_price'] = self.product.purchase_price
        initial['package_type'] = self.product.package_type
        initial['supplier'] = self.product.supplier.factory_name
        initial['supplier_sku'] = self.product.supplier_sku
        for option in self.option_names:
            initial['opt_' + option] = self.product.options[option]
        return initial

    def form_valid(self, form):
        form.save()
        messages.add_message(
            self.request, messages.SUCCESS, 'Product Updated')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'inventory:product', kwargs={'product_id': self.product_id})

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['product'] = self.product
        if 'Linn Title' in self.option_names:
            context_data['linnworks_title'] = self.product.linn_title
        if 'Linn SKU' in self.option_names:
            context_data['linnworks_sku'] = self.product.linn_sku
        department = self.product.department
        try:
            warehouse = models.Warehouse.objects.get(name=department)
        except models.Warehouse.DoesNotExist:
            context_data['warehouse_bays'] = []
        else:
            context_data['warehouse_bays'] = warehouse.bay_set.all()
        return context_data
