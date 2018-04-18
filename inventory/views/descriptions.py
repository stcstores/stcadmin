from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from inventory import forms
import cc_products

from .views import InventoryUserMixin


class DescriptionsView(InventoryUserMixin, FormView):
    form_class = forms.DescriptionForm
    template_name = 'inventory/descriptions.html'

    def dispatch(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = cc_products.get_range(self.range_id)
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        first_product = self.product_range.products[0]
        initial['title'] = self.product_range.name
        initial['description'] = self.product_range.description
        initial['amazon_bullets'] = first_product.amazon_bullets
        initial['search_terms'] = first_product.amazon_search_terms
        return initial

    def form_valid(self, form):
        self.product_range.description = form.cleaned_data['description']
        self.product_range.name = form.cleaned_data['title']
        for product in self.product_range.products:
            product.amazon_bullets = form.cleaned_data['amazon_bullets']
            product.amazon_search_terms = form.cleaned_data['search_terms']
        messages.add_message(
            self.request, messages.SUCCESS, 'Description Updated')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'inventory:descriptions', kwargs={'range_id': self.range_id})

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['product_range'] = self.product_range
        return context_data
