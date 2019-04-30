"""Forms for inventory app."""

from django import forms

from inventory import models
from inventory.cloud_commerce_updater import ProductUpdater
from product_editor.editor_manager import ProductEditorBase
from product_editor.forms import fields


class ProductRangeForm(forms.Form):
    """Form for editing a Product Range."""

    end_of_line = forms.BooleanField(
        required=False,
        help_text=(
            "Ranges are maked as <b>end of line</b> if the entire range is"
            " out of stock and unlikely to be re-ordered."
        ),
    )


class DescriptionForm(forms.Form):
    """Form for editing attributes that are the same across a range."""

    title = fields.Title()
    department = fields.Department()
    description = fields.Description()
    amazon_bullets = fields.AmazonBulletPoints()
    search_terms = fields.AmazonSearchTerms()


class CreateBayForm(forms.Form):
    """Form for creating new Warehouse Bays."""

    BACKUP = "backup"
    PRIMARY = "primary"
    BAY_TYPE_CHOICES = ((PRIMARY, "Primary"), (BACKUP, "Backup"))

    def __init__(self, *args, **kwargs):
        """Add fields to form."""
        super().__init__(*args, **kwargs)
        self.fields["department"] = fields.Department(label="Department")
        self.fields[
            "department"
        ].help_text = "The department to which the bay's contents belong."
        self.fields["name"] = forms.CharField(max_length=255, required=True)
        self.fields["name"].help_text = "The name of the bay to be created."
        self.fields["bay_type"] = forms.ChoiceField(
            choices=self.BAY_TYPE_CHOICES,
            widget=forms.RadioSelect,
            required=True,
            initial=self.PRIMARY,
        )
        self.fields[
            "bay_type"
        ].help_text = "Is this a primary picking location or backup bay?"
        self.fields["location"] = fields.Department(label="Location")
        self.fields["location"].help_text = "The physical location of the bay."
        self.fields["location"].required = False

    def clean(self, *args, **kwargs):
        """Create correct name for bay and ensure it does not already exist."""
        data = super().clean(*args, **kwargs)
        data["warehouse"] = models.Warehouse.objects.get(
            warehouse_ID=data["department"]
        )
        if data["bay_type"] == self.BACKUP:
            if not data["location"]:
                self.add_error("location", "Location is required for backup bays.")
                return
            data["backup_location"] = models.Warehouse.objects.get(
                warehouse_ID=data["location"]
            )
            self.new_bay = models.Bay.new_backup_bay(
                name=data["name"],
                department=data["warehouse"],
                backup_location=data["backup_location"],
            )
        else:
            self.new_bay = models.Bay(name=data["name"], warehouse=data["warehouse"])
        self.new_bay.clean()
        self.new_bay.validate_unique()
        return data

    def save(self):
        """Create Warehouse Bay."""
        self.new_bay.save()


class ImagesForm(forms.Form):
    """Form for adding product images."""

    product_ids = forms.CharField(widget=forms.HiddenInput)
    cloud_commerce_images = forms.ImageField(
        required=False,
        label="Cloud Commerce Images",
        widget=forms.ClearableFileInput(
            attrs={"multiple": True, "accept": ".jpg, .png"}
        ),
    )
    stcadmin_images = forms.ImageField(
        required=False,
        label="STC Admin Images",
        widget=forms.ClearableFileInput(
            attrs={"multiple": True, "accept": ".jpg, .png"}
        ),
    )


class ProductForm(ProductEditorBase, forms.Form):
    """Form for editing indivdual Products."""

    def __init__(self, *args, **kwargs):
        """Configure form fields."""
        self.product = kwargs.pop("product")
        super().__init__(*args, **kwargs)
        self.fields[self.SUPPLIER_SKU] = fields.SupplierSKU()
        self.fields[self.SUPPLIER] = fields.Supplier()
        self.fields[self.PURCHASE_PRICE] = fields.PurchasePrice()
        self.fields[self.VAT_RATE] = fields.VATRate()
        self.fields[self.PRICE] = fields.Price()
        self.fields[self.RETAIL_PRICE] = fields.RetailPrice()
        self.fields[self.LOCATION] = fields.WarehouseBayField()
        self.fields[self.PACKAGE_TYPE] = fields.PackageType()
        self.fields[self.INTERNATIONAL_SHIPPING] = fields.InternationalShipping()
        self.fields[self.WEIGHT] = fields.Weight()
        self.fields[self.DIMENSIONS] = fields.Dimensions()
        self.fields[self.GENDER] = fields.Gender()
        self.initial = self.get_initial()

    def get_initial(self):
        """Get initial values for form."""
        initial = {}
        initial[self.PRICE] = self.product.price
        initial[self.VAT_RATE] = self.product.VAT_rate
        bays = self.product.bays.all()
        warehouses = list(set([bay.warehouse for bay in bays]))
        if len(warehouses) > 1:
            self.add_error(self.LOCATIONS, "Mixed warehouses.")
        elif len(warehouses) == 1:
            initial[self.LOCATION] = {
                self.WAREHOUSE: warehouses[0].warehouse_ID,
                self.BAYS: [bay.bay_ID for bay in bays],
            }
        initial[self.DIMENSIONS] = {
            self.WIDTH: self.product.width_mm,
            self.HEIGHT: self.product.height_mm,
            self.LENGTH: self.product.length_mm,
        }
        initial[self.WEIGHT] = self.product.weight_grams
        initial[self.PURCHASE_PRICE] = self.product.purchase_price
        initial[self.RETAIL_PRICE] = self.product.retail_price
        initial[self.PACKAGE_TYPE] = self.product.package_type
        if self.product.supplier:
            initial[self.SUPPLIER] = self.product.supplier
        initial[self.SUPPLIER_SKU] = self.product.supplier_SKU
        initial[self.INTERNATIONAL_SHIPPING] = self.product.international_shipping
        initial[self.GENDER] = self.product.gender
        return initial

    def clean(self):
        """Clean submitted data."""
        cleaned_data = super().clean()
        cleaned_data[self.BAYS] = models.Bay.objects.filter(
            bay_ID__in=cleaned_data[self.LOCATION][self.BAYS]
        )
        return cleaned_data

    def save(self, *args, **kwargs):
        """Update product."""
        data = self.cleaned_data
        updater = ProductUpdater(self.product)
        updater.set_price(data[self.PRICE])
        updater.set_VAT_rate(data[self.VAT_RATE])
        updater.set_bays(data[self.BAYS])
        updater.set_width(data[self.DIMENSIONS][self.WIDTH])
        updater.set_height(data[self.DIMENSIONS][self.HEIGHT])
        updater.set_length(data[self.DIMENSIONS][self.LENGTH])
        updater.set_weight(data[self.WEIGHT])
        updater.set_package_type(data[self.PACKAGE_TYPE])
        updater.set_international_shipping(data[self.INTERNATIONAL_SHIPPING])
        updater.set_purchase_price(data[self.PURCHASE_PRICE])
        updater.set_retail_price(data[self.RETAIL_PRICE])
        updater.set_supplier(data[self.SUPPLIER])
        updater.set_supplier_SKU(data[self.SUPPLIER_SKU])
        updater.set_gender(data[self.GENDER])
