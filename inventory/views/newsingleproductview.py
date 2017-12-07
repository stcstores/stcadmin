from django.shortcuts import redirect
from django.views.generic.edit import FormView
from inventory.forms import NewSingleProductForm
from inventory.product_creator import SingleProduct

from .views import InventoryUserMixin


class NewSingleProductView(InventoryUserMixin, FormView):
    template_name = 'inventory/new_product/single_product_form.html'
    form_class = NewSingleProductForm

    def form_valid(self, form):
        new_product = SingleProduct(form.cleaned_data)
        return redirect(
            'inventory:product_range', new_product.product_range.id)
