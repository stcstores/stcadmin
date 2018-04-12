from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from home.views import UserInGroupMixin
from inventory import forms


class InventoryUserMixin(UserInGroupMixin):
    groups = ['inventory']


class NewProductView(InventoryUserMixin, TemplateView):
    template_name = 'inventory/new_product/new_product.html'


class SKUGeneratorView(InventoryUserMixin, TemplateView):
    template_name = 'inventory/sku_generator.html'


class CreateSupplierView(InventoryUserMixin, FormView):
    form_class = forms.CreateSupplierForm
    template_name = 'inventory/create_supplier.html'

    def form_valid(self, form):
        form.save()
        messages.add_message(
            self.request, messages.SUCCESS,
            'Created supplier {}'.format(form.cleaned_data['supplier_name']))
        return redirect('inventory:create_supplier')


class CreateBayView(InventoryUserMixin, FormView):
    form_class = forms.CreateBayForm
    template_name = 'inventory/new_bay.html'

    def form_valid(self, form):
        form.save()
        messages.add_message(
            self.request, messages.SUCCESS, 'Created bay {}'.format(form.bay))
        return redirect('inventory:new_bay')
