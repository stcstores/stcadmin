import cc_products
from django import forms
from inventory import models
from inventory.forms.new_product.fields import Location
from stcadmin.forms import KwargFormSet


class LocationsForm(forms.Form):
    product_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'product_id'}))
    product_name = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={'size': 200, 'class': 'product_title'}))
    stock_level = forms.CharField(required=False)
    warehouse = forms.ChoiceField(choices=[])
    locations = Location()

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop('product_id')
        self.product = cc_products.get_product(self.product_id)
        super().__init__(*args, **kwargs)
        warehouse_choices = [('', '')] + [
            (w.id, w.name) for w in models.Warehouse.objects.all()]
        self.fields['warehouse'] = forms.ChoiceField(
            choices=warehouse_choices, required=True)
        self.initial.update(self.get_initial())

    def get_initial(self):
        initial = {}
        initial['product_id'] = self.product_id
        initial['product_name'] = self.product.full_name
        initial['stock_level'] = self.product.stock_level
        initial['locations'] = [
            bay.id for bay in models.Bay.objects.filter(
                bay_id__in=self.product.bays)]
        warehouse = self.get_warehouse_for_bays(
            initial['locations'])
        if warehouse is None:
            initial['warehouse'] = None
        else:
            initial['warehouse'] = warehouse.id
        return initial

    def get_warehouse_for_bays(self, bay_ids):
        if len(bay_ids) == 0:
            return None
        bays = models.Bay.objects.filter(
            bay_id__in=[int(bay_id) for bay_id in bay_ids]).all()
        if all([bay.warehouse == bays[0].warehouse for bay in bays]):
            return bays[0].warehouse
        return None

    def save(self):
        self.product.bays = self.cleaned_data['locations']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['bays'] = [
            bay.name for bay in models.Bay.objects.filter(
                bay_id__in=self.product.bays)]
        return context


class LocationsFormSet(KwargFormSet):
    form = LocationsForm
