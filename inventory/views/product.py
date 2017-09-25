from ccapi import CCAPI
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from inventory import forms
from inventory.forms.new_product import fields

from .views import InventoryUserMixin


class Product(InventoryUserMixin, FormView):
    template_name = 'inventory/product.html'
    form_class = forms.ProductForm

    def dispatch(self, *args, **kwargs):
        self.product_id = self.kwargs.get('product_id')
        self.product = CCAPI.get_product(self.product_id)
        self.product_range = CCAPI.get_range(self.product.range_id)
        self.option_names = [
            option.option_name for option in self.product_range.options]
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = self.product
        kwargs['product_range'] = self.product_range
        kwargs['option_names'] = self.option_names
        return kwargs

    def get_option_value(self, option_name):
        try:
            return self.product.options[option_name].value
        except KeyError:
            return ''

    def get_initial(self):
        initial = super().get_initial()
        initial['vat_rate'] = fields.VATRate.get_VAT_percentage(
            self.product.vat_rate_id)
        initial['price'] = self.product.base_price
        initial['weight'] = self.product.weight
        initial['height'] = self.product.height_mm
        initial['length'] = self.product.length_mm
        initial['width'] = self.product.width_mm
        initial['purchase_price'] = self.get_option_value('Purchase Price')
        initial['package_type'] = self.get_option_value('Package Type')
        initial['supplier_sku'] = self.get_option_value('Supplier SKU')
        for option in self.option_names:
            initial['opt_' + option] = self.get_option_value(option)
        return initial

    def form_valid(self, form):
        data = form.cleaned_data
        self.product.set_vat_rate(data['vat_rate'])
        self.product.set_base_price(data['price'])
        self.product.set_option_value('Package Type', data['package_type'])
        self.product.set_product_scope(
            weight=data['weight'], height=data['height'],
            length=data['length'], width=data['width'],
            large_letter_compatible=data['package_type'] == 'Large Letter')
        if len(data['supplier_sku']) > 0:
            self.product.set_option_value(
                'Supplier SKU', data['supplier_sku'], create=True)
        if len(data['purchase_price']) > 0:
            self.product.set_option_value(
                'Purchase Price', data['purchase_price'], create=True)
        for option_field in form.option_names:
            value = data['opt_' + option_field]
            if len(value) > 0:
                self.product.set_option_value(option_field, value, create=True)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'inventory:product', kwargs={'product_id': self.product_id})

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['product'] = self.product
        return context_data
