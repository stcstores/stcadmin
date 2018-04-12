import cc_products
from django import forms

from inventory import models
from inventory.forms.new_product.fields import Department, Location
from stcadmin.forms import KwargFormSet


class DepartmentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.product_range = kwargs.pop('product_range')
        super().__init__(*args, **kwargs)
        self.fields['department'] = Department()
        self.initial.update(self.get_initial())

    def get_initial(self):
        initial = {}
        try:
            department = self.product_range.department
        except cc_products.exceptions.DepartmentError:
            department = None
        if department is None:
            department_id = None
        else:
            try:
                department_id = models.Warehouse.used_warehouses.get(
                    name=department).warehouse_id
            except models.DoesNotExist:
                department_id = None
        initial['department'] = department_id
        return initial

    def save(self):
        self.product_range.department = self.cleaned_data['department']


class LocationsForm(forms.Form):
    product_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'product_id'}))
    product_name = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={'size': 200, 'class': 'product_title'}))
    stock_level = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product')
        super().__init__(*args, **kwargs)
        self.fields['locations'] = Location()
        self.initial.update(self.get_initial())

    def get_initial(self):
        initial = {}
        initial['product_id'] = self.product.id
        initial['product_name'] = self.product.full_name
        initial['stock_level'] = self.product.stock_level
        initial['locations'] = [
            bay.id for bay in models.Bay.objects.filter(
                bay_id__in=self.product.bays)]
        return initial

    def get_warehouse_for_bays(self, bay_ids):
        if len(bay_ids) == 0:
            return None
        bays = models.Bay.objects.filter(
            bay_id__in=[int(bay_id) for bay_id in bay_ids]).all()
        if all([bay.warehouse == bays[0].warehouse for bay in bays]):
            return bays[0].warehouse
        return None

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data.pop('product_name')
        cleaned_data.pop('stock_level')
        bays = self.cleaned_data['locations']
        if len(bays) == 0:
            bays = [self.warehouse.default_bay.bay_id]
        cleaned_data['bays'] = bays
        return cleaned_data

    def save(self):
        self.product.bays = self.cleaned_data['bays']

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['bays'] = [
            bay.name for bay in models.Bay.objects.filter(
                bay_id__in=self.product.bays)]
        return context


class LocationsFormSet(KwargFormSet):
    form = LocationsForm
