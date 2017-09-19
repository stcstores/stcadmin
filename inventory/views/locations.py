from ccapi import CCAPI, Warehouses
from django.shortcuts import redirect, render
from django.views.generic.edit import FormView
from inventory.forms import LocationsFormSet

from .views import InventoryUserMixin


class LocationForm(InventoryUserMixin, FormView):

    template_name = 'inventory/locations.html'
    form_class = LocationsFormSet

    def dispatch(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = CCAPI.get_range(self.range_id)
        return super().dispatch(*args, **kwargs)

    def post(self, request, range_id):
        if request.method == 'POST':
            formset = self.form_class(request.POST, request.FILES)
            if formset.is_valid():
                self.is_valid(formset)
                return redirect('inventory:product_range', range_id)
        else:
            formset = self.form_class(initial=self.get_initial())
        return render(
            request, self.template_name, {
                'formset': formset, 'product_range': self.product_range})

    def get(self, request, range_id):
        formset = self.form_class(initial=self.get_initial())
        return render(
            request, self.template_name,
            {
                'formset': formset, 'bays': self.bays,
                'product_range': self.product_range})

    def get_initial(self):
        self.products = self.product_range.products
        for product in self.products:
            product_bays = CCAPI.get_bays_for_product(product.id)
            if product_bays is None:
                product.bays = []
            else:
                product.bays = product_bays
        initial = [
            {
                'product_id': product.id,
                'product_name': product.full_name,
                'stock_level': product.stock_level,
                'locations': [bay.name for bay in product.bays],
            } for product in self.products]
        if len(product.bays) > 0:
            warehouse_id = product.bays[0].warehouse_id
            self.warehouse = [
                warehouse for warehouse in Warehouses if
                warehouse.id == warehouse_id][0]
            self.bays = [bay.name for bay in self.warehouse.bays]
            self.bays.sort()
        else:
            self.bays = []
        return initial

    def is_valid(self, forms):
        for form in forms:
            data = form.cleaned_data
            product = CCAPI.get_product(data['product_id'])
            new_bay_names = [location for location in data['locations']]
            self.update_bays(product, new_bay_names)

    def update_bays(self, product, new_bay_names):
        warehouse_name = str(product.options['Department'].value)
        existing_bays = product.bays
        if existing_bays is None:
            existing_bays = []
        existing_bay_ids = [bay.id for bay in existing_bays]
        new_bay_ids = [
            CCAPI.get_bay_id(bay_name, warehouse_name, create=True) for
            bay_name in new_bay_names]
        for new_bay_id in new_bay_ids:
            if new_bay_id not in existing_bay_ids:
                product.add_bay(new_bay_id)
        for existing_bay_id in existing_bay_ids:
            if existing_bay_id not in new_bay_ids:
                product.remove_bay(existing_bay_id)
