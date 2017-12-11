import threading

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from inventory.forms import NewSingleProductForm
from inventory.product_creator import SingleProduct, create_variations

from .views import InventoryUserMixin


class NewSingleProductView(InventoryUserMixin, FormView):
    template_name = 'inventory/new_product/single_product_form.html'
    form_class = NewSingleProductForm

    def form_valid(self, form):
        new_product = SingleProduct(form.cleaned_data)
        t = threading.Thread(target=create_variations, args=[new_product])
        t.setDaemon(True)
        t.start()
        messages.add_message(
            self.request, messages.SUCCESS,
            ("Your product has been submitted but may take some time to "
             "complete. Please check back later."))
        return redirect(
            'inventory:product_range', new_product.product_range.id)
