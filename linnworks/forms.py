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
        item = pylinnworks.Inventory.get_item_by_stock_ID(stock_id)
        default_location = pylinnworks.Settings.get_location_by_name('Default')
        item.get_locations().add_location(default_location)


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
    bin_rack = forms.CharField(label='Bin/Rack')
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
            self.fields['bin_rack'].initial = self.get_item_bin_rack()

    def get_item_bin_rack(self):
        location = self.get_item_default_location()
        return location.bin_rack

    def set_item_bin_rack(self, bin_rack):
        location = self.get_item_default_location()
        location.bin_rack = bin_rack
        location.save()

    def get_item_default_location(self):
        if self.item.locations is None:
            self.item.get_locations()
        try:
            location = self.item.locations.get_location_by_name('Default')
        except:
            raise
            default_location = pylinnworks.Settings.get_location_by_name(
                'Default')
            self.item.locations.add_location(default_location)
            location = self.item.locations.get_location_by_name('Default')
        return location

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
        self.set_item_bin_rack(data['bin_rack'])
        self.item.save()
