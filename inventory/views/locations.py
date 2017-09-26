from ccapi import CCAPI, Warehouses
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from inventory.forms import LocationsFormSet

from .views import InventoryUserMixin


class LocationFormView(InventoryUserMixin, FormView):

    template_name = 'inventory/locations.html'
    form_class = LocationsFormSet

    def dispatch(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = CCAPI.get_range(self.range_id)
        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'inventory:locations', kwargs={'range_id': self.range_id})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['formset'] = context.pop('form')
        context['product_range'] = self.product_range
        return context

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

    def form_valid(self, forms):
        for form in forms:
            data = form.cleaned_data
            product = CCAPI.get_product(data['product_id'])
            new_bay_names = [location for location in data['locations']]
            self.update_bays(product, new_bay_names)
        return super().form_valid(form)

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
