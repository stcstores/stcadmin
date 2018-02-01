from ccapi import CCAPI
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from inventory import forms

from .views import InventoryUserMixin


class ProductView(InventoryUserMixin, FormView):
    template_name = 'inventory/product.html'
    form_class = forms.ProductForm

    def dispatch(self, *args, **kwargs):
        self.product_id = self.kwargs.get('product_id')
        self.product = CCAPI.get_product(self.product_id)
        self.product_range = CCAPI.get_range(self.product.range_id)
        self.option_names = [
            option.option_name for option in self.product_range.options]
        self.product.bays = CCAPI.get_bays_for_product(self.product.id) or []
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
        initial['vat_rate'] = self.product.vat_rate
        initial['price'] = self.product.base_price
        initial['locations'] = [bay.name for bay in self.product.bays]
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
        new_bay_names = form.cleaned_data['locations']
        existing_bays = self.product.bays
        existing_bay_ids = [b.id for b in existing_bays]
        department = self.get_option_value('Department').value
        new_bay_ids = [
            CCAPI.get_bay_id(bay_name, department, create=True) for
            bay_name in new_bay_names]
        for new_bay_id in new_bay_ids:
            if new_bay_id not in existing_bay_ids:
                self.product.add_bay(new_bay_id)
        for existing_bay_id in existing_bay_ids:
            if existing_bay_id not in new_bay_ids:
                self.product.remove_bay(existing_bay_id)
        messages.add_message(
            self.request, messages.SUCCESS, 'Product Updated')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'inventory:product', kwargs={'product_id': self.product_id})

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        warehouses = CCAPI.get_warehouses()
        context_data['product'] = self.product
        if 'Linn Title' in self.option_names:
            context_data['linnworks_title'] = self.get_option_value(
                'Linn Title')
        if 'Linn SKU' in self.option_names:
            context_data['linnworks_sku'] = self.get_option_value('Linn SKU')
        department = self.get_option_value('Department').value
        context_data['warehouse_bays'] = [
            bay.name for bay in warehouses[department]]
        return context_data
