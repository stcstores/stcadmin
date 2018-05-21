"""Forms for inventory app."""

from ccapi import CCAPI
from django import forms

from inventory import models
from product_editor.editor_manager import ProductEditorBase
from product_editor.forms import fields
from product_editor.forms.fields import Description, Title


class ProductRangeForm(forms.Form):
    """Form for editing a Product Range."""

    end_of_line = forms.BooleanField(
        required=False,
        help_text=(
            'Ranges are maked as <b>end of line</b> if the entire range is'
            ' out of stock and unlikely to be re-ordered.'))


class DescriptionForm(forms.Form):
    """Form for editing attributes that are the same across a range."""

    title = Title()
    description = Description()
    amazon_bullets = fields.AmazonBulletPoints()
    search_terms = fields.AmazonSearchTerms()


class CreateSupplierForm(forms.Form):
    """Form for creating new suppliers."""

    supplier_name = forms.CharField(max_length=255)
    SUPPLIER_OPTION_ID = 35131

    def clean(self):
        """Verify supplier does not already exist."""
        cleaned_data = super().clean()
        factories = CCAPI.get_factories()
        factory_names = [f.name for f in factories]
        if cleaned_data['supplier_name'] in factory_names:
            self.add_error('supplier_name', 'Supplier already exists.')

    def save(self):
        """Create new supplier."""
        name = self.cleaned_data['supplier_name']
        CCAPI.create_factory(name)
        CCAPI.get_option_value_id(self.SUPPLIER_OPTION_ID, name, create=True)


class CreateBayForm(forms.Form):
    """Form for creating new Warehouse Bays."""

    BACKUP = 'backup'
    PRIMARY = 'primary'
    BAY_TYPE_CHOICES = ((PRIMARY, 'Primary'), (BACKUP, 'Backup'))

    def __init__(self, *args, **kwargs):
        """Add fields to form."""
        super().__init__(*args, **kwargs)
        self.fields['department'] = fields.Department(label='Department')
        self.fields['department'].help_text = (
            "The department to which the bay's contents belong.")
        self.fields['name'] = forms.CharField(max_length=255, required=True)
        self.fields['name'].help_text = 'The name of the bay to be created.'
        self.fields['bay_type'] = forms.ChoiceField(
            choices=self.BAY_TYPE_CHOICES, widget=forms.RadioSelect,
            required=True, initial=self.PRIMARY)
        self.fields['bay_type'].help_text = (
            'Is this a primary picking location or backup bay?')
        self.fields['location'] = fields.Department(label='Location')
        self.fields['location'].help_text = 'The physical location of the bay.'
        self.fields['location'].required = False

    def clean(self, *args, **kwargs):
        """Create correct name for bay and ensure it does not already exist."""
        data = super().clean(*args, **kwargs)
        if data['bay_type'] == self.BACKUP:
            if not data['location']:
                self.add_error(
                    'location', 'Location is required for backup bays.')
                return
        if data['bay_type'] == self.PRIMARY:
            warehouse = models.Warehouse.objects.get(
                warehouse_id=data['department'])
            data['bay_name'] = data['name']
        else:
            warehouse = models.Warehouse.objects.get(
                warehouse_id=data['department'])
            location = models.Warehouse.objects.get(
                warehouse_id=data['location'])
            data['bay_name'] = '{} Backup {} {}'.format(
                warehouse.abriviation, location.name, data['name'])
        data['warehouse_id'] = warehouse.warehouse_id
        data['warehouse_name'] = warehouse.name
        if models.Bay.objects.filter(name=data['bay_name']).exists():
            self.add_error('name', 'Bay name already exists.')
        return data

    def save(self):
        """Create Warehouse Bay."""
        warehouse_id = self.cleaned_data['warehouse_id']
        warehouse = models.Warehouse.objects.get(warehouse_id=warehouse_id)
        bay_name = self.cleaned_data['bay_name']
        bay_id = CCAPI.get_bay_id(bay_name, warehouse.name, create=True)
        self.bay = models.Bay(
            bay_id=bay_id, warehouse=warehouse, name=bay_name)
        self.bay.save()


class ImagesForm(forms.Form):
    """Form for adding product images."""

    product_ids = forms.CharField(widget=forms.HiddenInput)
    cloud_commerce_images = forms.ImageField(
        required=False,
        label='Cloud Commerce Images',
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'accept': '.jpg, .png'}))
    stcadmin_images = forms.ImageField(
        required=False,
        label='STC Admin Images',
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'accept': '.jpg, .png'}))


class ProductForm(ProductEditorBase, forms.Form):
    """Form for editing indivdual Products."""

    ignore_options = [
        'Department', 'Brand', 'Manufacturer', 'WooCategory1', 'WooCategory2',
        'WooCategory3', 'International Shipping', 'Package Type', 'Supplier',
        'Purchase Price', 'Date Created', 'Location', 'Supplier SKU',
        'Amazon Bullets', 'Amazon Search Terms', 'Linn SKU', 'Linn Title',
        'Retail Price']

    def __init__(self, *args, **kwargs):
        """Configure form fields."""
        self.product = kwargs.pop('product')
        self.product_range = kwargs.pop('product_range')
        options = kwargs.pop('options')
        self.options = {
            o: v for o, v in options.items() if o not in self.ignore_options}
        super().__init__(*args, **kwargs)
        self.fields[self.PRICE] = fields.VATPrice()
        self.fields[self.LOCATION] = fields.WarehouseBayField()
        self.fields[self.WEIGHT] = fields.Weight()
        self.fields[self.DIMENSIONS] = fields.Dimensions()
        self.fields[self.PACKAGE_TYPE] = fields.PackageType()
        self.fields[self.PURCHASE_PRICE] = fields.PurchasePrice()
        self.fields[self.RETAIL_PRICE] = fields.RetailPrice()
        self.fields[self.SUPPLIER] = fields.Supplier()
        self.fields[self.SUPPLIER_SKU] = fields.SupplierSKU()
        for option_name, values in self.options.items():
            choices = [('', '')] + [
                (v, v) for v in self.get_choice_values(option_name, values)]
            self.fields['opt_' + option_name] = fields.ListingOption(
                choices=choices, label=option_name)
        self.initial = self.get_initial()

    def get_initial(self):
        """Get initial values for form."""
        initial = {}
        initial[self.PRICE] = {
            self.VAT_RATE: self.product.vat_rate,
            self.EX_VAT: self.product.price,
            'with_vat_price': None}
        bays = [
            bay for bay in models.Bay.objects.filter(
                bay_id__in=self.product.bays)]
        warehouses = list(set([bay.warehouse for bay in bays]))
        if len(warehouses) > 1:
            self.add_error(self.LOCATIONS, 'Mixed warehouses.')
        elif len(warehouses) == 1:
            initial[self.LOCATION] = {
                self.WAREHOUSE: warehouses[0].warehouse_id,
                self.BAYS: [bay.id for bay in bays]}
        initial[self.DIMENSIONS] = {
            self.WIDTH: self.product.width,
            self.HEIGHT: self.product.height,
            self.LENGTH: self.product.length}
        initial[self.WEIGHT] = self.product.weight
        initial[self.PURCHASE_PRICE] = self.product.purchase_price
        initial[self.RETAIL_PRICE] = self.product.retail_price
        initial[self.PACKAGE_TYPE] = self.product.package_type
        if self.product.supplier:
            initial[self.SUPPLIER] = self.product.supplier.factory_name
        initial[self.SUPPLIER_SKU] = self.product.supplier_sku
        for option in self.options:
            initial['opt_' + option] = self.product.options[option]
        return initial

    def get_choice_values(self, option_name, values):
        """Return choices for option field."""
        if option_name in self.initial:
            if self.initial[option_name] not in values:
                values.append(self.initial[option_name])
        return values

    def save(self, *args, **kwargs):
        """Update product."""
        data = self.cleaned_data
        self.product.vat_rate = data[self.PRICE][self.VAT_RATE]
        self.product.price = data[self.PRICE][self.EX_VAT]
        self.product.bays = data[self.LOCATION][self.BAYS]
        self.product.width = data[self.DIMENSIONS][self.WIDTH]
        self.product.height = data[self.DIMENSIONS][self.HEIGHT]
        self.product.length = data[self.DIMENSIONS][self.LENGTH]
        self.product.weight = data[self.WEIGHT]
        self.product.package_type = data[self.PACKAGE_TYPE]
        self.product.purchase_price = data[self.PURCHASE_PRICE]
        self.product.retail_price = data[self.RETAIL_PRICE]
        self.product.supplier = data[self.SUPPLIER]
        self.product.supplier_sku = data[self.SUPPLIER_SKU]
        options = [key[4:] for key in data.keys() if key[:4] == 'opt_']
        for option in options:
            value = data['opt_' + option]
            self.product.options[option] = value
