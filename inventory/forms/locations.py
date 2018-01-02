from ccapi import CCAPI
from django import forms
from list_input import ListInput
from stcadmin.forms import KwargFormSet


class LocationsForm(forms.Form):
    product_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'product_id'}))
    product_name = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={'size': 200, 'class': 'product_title'}))
    stock_level = forms.CharField(required=False)
    warehouse = forms.ChoiceField(
        choices=[(w.id, w.name) for w in CCAPI.get_warehouses()])
    locations = ListInput(required=True)

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop('product_id')
        self.warehouses = kwargs.pop('warehouses')
        self.product = CCAPI.get_product(self.product_id)
        self.get_bays()
        super().__init__(*args, **kwargs)
        self.fields['warehouse'] = forms.ChoiceField(
            choices=[(w.id, w.name) for w in self.warehouses])
        self.initial.update(self.get_initial())

    def get_initial(self):
        initial = {}
        initial['product_id'] = self.product_id
        initial['product_name'] = self.product.full_name
        initial['stock_level'] = self.product.stock_level
        initial['warehouse'] = self.product.bays[0].warehouse_id
        initial['locations'] = [bay.name for bay in self.product.bays]
        return initial

    def get_bays(self):
        product_bays = CCAPI.get_bays_for_product(self.product.id)
        if product_bays is None:
            self.product.bays = []
        else:
            self.product.bays = product_bays

    def get_warehouse_name_by_ID(self, warehouse_id):
        return {w.id: w for w in self.warehouses}[int(warehouse_id)].name

    def save(self):
        warehouse_name = self.get_warehouse_name_by_ID(
            self.cleaned_data['warehouse'])
        new_bay_names = self.cleaned_data['locations']
        existing_bays = self.product.bays
        existing_bay_ids = [b.id for b in existing_bays]
        new_bay_ids = [
            CCAPI.get_bay_id(bay_name, warehouse_name, create=True) for
            bay_name in new_bay_names]
        for new_bay_id in new_bay_ids:
            if new_bay_id not in existing_bay_ids:
                self.product.add_bay(new_bay_id)
        for existing_bay_id in existing_bay_ids:
            if existing_bay_id not in new_bay_ids:
                self.product.remove_bay(existing_bay_id)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['bays'] = [bay.name for bay in self.product.bays]
        return context


class LocationsFormSet(KwargFormSet):
    form = LocationsForm

    def __init__(self, *args, **kwargs):
        self.warehouses = {
            w.id: sorted([b.name for b in w.bays]) for w in
            CCAPI.get_warehouses()}
        super().__init__(*args, **kwargs)
