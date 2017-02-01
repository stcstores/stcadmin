import uuid

from django import forms
from stcadmin.settings import PYLINNWORKS_CONFIG
import pylinnworks


class NewItemForm(forms.Form):
    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    new_sku = pylinnworks.Inventory.get_new_SKU()
    stock_id = forms.CharField(
        initial=str(uuid.uuid4()), required=True, disabled=True,
        label='Stock ID', widget=forms.TextInput(attrs={'size': '40'}))
    sku = forms.CharField(
        initial=new_sku, required=True, label='SKU', disabled=True)
    title = forms.CharField(
        required=True, widget=forms.TextInput(attrs={'size': '40'}))
    barcode = forms.CharField()

    def save(self):
        stock_id = self.cleaned_data['stock_id']
        sku = self.cleaned_data['sku']
        title = self.cleaned_data['title']
        barcode = self.cleaned_data['barcode']
        pylinnworks.Inventory.create_new_item(
            stock_id=stock_id, sku=sku, title=title, barcode=barcode)


class EditItemForm(forms.Form):

    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    settings = pylinnworks.Settings
    CATEGORIES = [
        [category.guid, category.name] for category in
        settings.get_categories()]
    SHIPPING_METHODS = [
        [method.guid, method.name] for method in
        settings.get_shipping_methods()]
    stock_id = forms.CharField(
        required=True, disabled=True, label='Stock ID',
        widget=forms.TextInput(attrs={'size': '40'}))
    sku = forms.CharField(required=True, label='SKU', disabled=True)
    title = forms.CharField(
        required=True, widget=forms.TextInput(attrs={'size': '40'}))
    barcode = forms.CharField()
    retail_price = forms.DecimalField(max_digits=6, decimal_places=2)
    purchase_price = forms.DecimalField(max_digits=6, decimal_places=2)
    category = forms.ChoiceField(choices=CATEGORIES)
    shipping_method = forms.ChoiceField(choices=SHIPPING_METHODS)
    description = forms.CharField(
        widget=forms.widgets.Textarea, required=False)
    weight = forms.IntegerField(required=True)
    width = forms.IntegerField()
    height = forms.IntegerField()
    depth = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        stock_id = kwargs.pop('stock_id', None)
        super().__init__(*args, **kwargs)
        if stock_id is not None:
            self.item = pylinnworks.Inventory.get_item_by_stock_ID(stock_id)
            self.fields['stock_id'].initial = self.item.stock_id
            self.fields['sku'].initial = self.item.sku
            self.fields['title'].initial = self.item.title
            self.fields['barcode'].initial = self.item.barcode
            self.fields['retail_price'].initial = self.item.retail_price
            self.fields['purchase_price'].initial = self.item.purchase_price
            self.fields['category'].initial = self.item.category.guid
            self.fields[
                'shipping_method'].initial = self.item.postal_service.guid
            self.fields['description'].initial = self.item.meta_data
            self.fields['weight'].initial = self.item.weight
            self.fields['width'].initial = self.item.width
            self.fields['height'].initial = self.item.height
            self.fields['depth'].initial = self.item.depth

    def save(self):
        data = self.cleaned_data
        self.item.title = data['title']
        self.item.barcode = data['barcode']
        self.item.retail_price = data['retail_price']
        self.item.purchase_price = data['purchase_price']
        self.item.category = self.settings.get_category_by_ID(
            data['category'])
        self.item.postal_service = self.settings.get_shipping_method_by_ID(
            data['shipping_method'])
        self.item.meta_data = data['description']
        self.item.weight = data['weight']
        self.item.width = data['width']
        self.item.height = data['height']
        self.item.depth = data['depth']
        self.item.save()
