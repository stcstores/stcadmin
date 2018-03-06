import cc_products
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from inventory.forms import VariationsFormSet

from .views import InventoryUserMixin


class VariationsFormView(InventoryUserMixin, FormView):

    template_name = 'inventory/variations.html'
    form_class = VariationsFormSet

    def dispatch(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = cc_products.get_range(self.range_id)
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['form_kwargs'] = [
            {'product': p} for p in self.product_range.products]
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'inventory:variations', kwargs={'range_id': self.range_id})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        formset = context.pop('form')
        context['formset'] = formset
        context['product_range'] = self.product_range
        return context

    def form_valid(self, forms):
        for form in forms:
            form.save()
        messages.add_message(
            self.request, messages.SUCCESS, 'Variations Updated')
        return super().form_valid(form)
