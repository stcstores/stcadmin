"""Miscellaneous views for inventory."""

from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from home.views import UserInGroupMixin
from inventory import forms


class InventoryUserMixin(UserInGroupMixin):
    """Mixin to validate user in in inventory group."""

    groups = ['inventory']


class SKUGeneratorView(InventoryUserMixin, TemplateView):
    """View for SKU Generator page."""

    template_name = 'inventory/sku_generator.html'


class CreateSupplierView(InventoryUserMixin, FormView):
    """View for Create Supplier page."""

    form_class = forms.CreateSupplierForm
    template_name = 'inventory/create_supplier.html'

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        form.save()
        messages.add_message(
            self.request, messages.SUCCESS,
            'Created supplier {}'.format(form.cleaned_data['supplier_name']))
        return redirect('inventory:create_supplier')


class CreateBayView(InventoryUserMixin, FormView):
    """View for Create Bay page."""

    form_class = forms.CreateBayForm
    template_name = 'inventory/create_warehouse_bay.html'

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        form.save()
        messages.add_message(
            self.request, messages.SUCCESS, 'Created bay {}'.format(form.bay))
        return redirect('inventory:create_warehouse_bay')
