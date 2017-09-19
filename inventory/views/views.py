from ccapi import CCAPI
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from home.views import UserInGroupMixin
from inventory import forms


class InventoryUserMixin(UserInGroupMixin):
    groups = ['inventory']


class Index(InventoryUserMixin, TemplateView):
    template_name = 'inventory/index.html'


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


class DescriptionEditor(InventoryUserMixin, FormView):
    form_class = forms.DescriptionForm
    template_name = 'inventory/description_editor.html'

    def dispatch(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = CCAPI.get_range(self.range_id)
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        first_product = CCAPI.get_product(self.product_range.products[0].id)
        initial['description'] = first_product.description
        return initial

    def form_valid(self, form):
        self.product_range.set_description(
            form.cleaned_data['description'], update_channels=True)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'inventory:product_range', kwargs={'range_id': self.range_id})

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['product_range'] = self.product_range
        return context_data
