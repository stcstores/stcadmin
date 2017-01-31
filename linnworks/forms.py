from django import forms
from stcadmin.settings import PYLINNWORKS_CONFIG
import pylinnworks


class EditItemForm(forms.Form):

    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    CATEGORIES = [
        [category.guid, category.name] for category in
        pylinnworks.Settings.get_categories()]
    SHIPPING_METHODS = [
        [method.guid, method.name] for method in
        pylinnworks.Settings.get_shipping_methods()]
    sku = forms.CharField(required=True, label='SKU')
    title = forms.CharField(required=True)
    barcode = forms.CharField()
    retail_price = forms.DecimalField(max_digits=6, decimal_places=2)
    purchase_price = forms.DecimalField(max_digits=6, decimal_places=2)
    category = forms.ChoiceField(choices=CATEGORIES)
    shipping_method = forms.ChoiceField(choices=SHIPPING_METHODS)
    description = forms.CharField(widget=forms.widgets.Textarea)
    weight = forms.IntegerField(required=True)
    width = forms.IntegerField()
    height = forms.IntegerField()
    depth = forms.IntegerField()
