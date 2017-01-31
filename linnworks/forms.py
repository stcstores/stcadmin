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

    def __init__(self, *args, **kwargs):
        item = kwargs.pop('item', None)
        super().__init__(*args, **kwargs)
        if item is not None:
            self.fields['sku'].initial = item.sku
            self.fields['title'].initial = item.title
            self.fields['barcode'].initial = item.barcode
            self.fields['retail_price'].initial = item.retail_price
            self.fields['purchase_price'].initial = item.purchase_price
            self.fields['category'].initial = item.category.guid
            self.fields['shipping_method'].initial = item.postal_service.guid
            self.fields['description'].initial = item.meta_data
            self.fields['weight'].initial = item.weight
            self.fields['width'].initial = item.width
            self.fields['height'].initial = item.height
            self.fields['depth'].initial = item.depth
