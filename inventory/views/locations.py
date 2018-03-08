import cc_products
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from inventory import models
from inventory.forms import DepartmentForm, LocationsFormSet

from .views import InventoryUserMixin


class LocationFormView(InventoryUserMixin, TemplateView):

    template_name = 'inventory/locations.html'

    def get(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = cc_products.get_range(self.range_id)
        self.department_form = DepartmentForm(
            product_range=self.product_range)
        self.bay_formset = LocationsFormSet(form_kwargs=[{
            'product': p} for p in self.product_range.products])
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = cc_products.get_range(self.range_id)
        self.department_form = DepartmentForm(
            self.request.POST, product_range=self.product_range)
        self.bay_formset = LocationsFormSet(self.request.POST, form_kwargs=[{
            'product': p} for p in self.product_range.products])
        if self.department_form.is_valid():
            self.department_form.save()
            for form in self.bay_formset:
                form.warehouse = models.Warehouse.used_warehouses.get(
                    name=self.department_form.cleaned_data['department'])
            if self.bay_formset.is_valid():
                for form in self.bay_formset:
                    form.save()
            messages.add_message(
                self.request, messages.SUCCESS, 'Locations Updated')
            return redirect(self.get_success_url())
        return super().get(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'inventory:locations', kwargs={'range_id': self.range_id})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['product_range'] = self.product_range
        context['department_form'] = self.department_form
        context['bay_formset'] = self.bay_formset
        return context

    def form_valid(self, forms):
        for form in forms:
            form.save()

        return super().form_valid(form)
