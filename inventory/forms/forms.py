"""Forms for inventory app."""

from django import forms
from django.db import transaction

from inventory import models
from product_editor.editor_manager import ProductEditorBase
from product_editor.forms import fields
from stcadmin.forms import KwargFormSet


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


class ProductForm(ProductEditorBase, forms.Form):
    """Form for editing indivdual Products."""

    def __init__(self, *args, **kwargs):
        """Configure form fields."""
        self.product = kwargs.pop("product")
        super().__init__(*args, **kwargs)
        self.fields[self.BRAND] = fields.Brand()
        self.fields[self.MANUFACTURER] = fields.Manufacturer()
        self.fields[self.BARCODE] = fields.Barcode()
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
        initial[self.BRAND] = self.product.brand
        initial[self.MANUFACTURER] = self.product.manufacturer
        initial[self.BARCODE] = self.product.barcode
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
        updater_class = kwargs["updater_class"]
        updater = updater_class(self.product)
        updater.set_brand(data[self.BRAND])
        updater.set_manufacturer(data[self.MANUFACTURER])
        updater.set_barcode(data[self.BARCODE])
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


class VariationForm(ProductForm):
    """Form for the variation page."""

    def __init__(self, *args, **kwargs):
        """Make the location field inline."""
        super().__init__(*args, **kwargs)
        self.fields[self.LOCATION] = fields.WarehouseBayField(inline=True)


class VariationsFormSet(KwargFormSet):
    """Formset for updating the locations of all Products within a Range."""

    form = VariationForm


class AddProductOption(forms.Form):
    """Add a new variation product option to a partial product range."""

    def __init__(self, *args, **kwargs):
        """Instanciate the form."""
        self.edit = kwargs.pop("edit")
        self.variation = kwargs.pop("variation")
        self.product_range = self.edit.partial_product_range
        super().__init__(*args, **kwargs)
        self.add_fields()

    def add_fields(self):
        """Add fields to the form."""
        self.fields["option"] = fields.SelectProductOption(
            product_range=self.product_range
        )
        for option_ID, name in self.fields["option"].choices:
            if not option_ID:
                continue
            self.fields[f"values_{option_ID}"] = fields.VariationOptions(
                product_option=models.ProductOption.objects.get(pk=option_ID),
                product_range=self.product_range,
                label=name,
                required=False,
            )

    def clean(self):
        """Ensure a new product option cannot be selected with fewer than two values."""
        cleaned_data = super().clean()
        values_field_name = f"values_{cleaned_data['option'].pk}"
        cleaned_data["values"] = cleaned_data[values_field_name]
        if self.variation is True and len(cleaned_data["values"]) < 2:
            self.add_error(
                values_field_name,
                "At least two variation options must be selected for each dropdown.",
            )
        return cleaned_data

    @transaction.atomic
    def save(self):
        """Save changes to the database."""
        product_option = self.cleaned_data["option"]
        product_option_values = self.cleaned_data["values"]
        models.PartialProductRangeSelectedOption(
            product_range=self.product_range,
            product_option=product_option,
            variation=self.variation,
            pre_existing=False,
        ).save()
        for value in product_option_values:
            self.edit.product_option_values.add(value)


class SetProductOptionValues(forms.Form):
    """Form for adding values for a new product option to a product."""

    def __init__(self, *args, **kwargs):
        """Set up form fields."""
        self.edit = kwargs.pop("edit")
        self.product_range = kwargs.pop("product_range")
        self.product = kwargs.pop("product")
        super().__init__(*args, **kwargs)
        self.fields["product_ID"] = forms.CharField(
            widget=forms.HiddenInput, required=True
        )
        self.options = self.product_range.product_options.all()
        self.variation_options = self.product_range.variation_options()
        self.listing_options = self.product_range.listing_options()
        for option in self.variation_options:
            self.add_option_field(option, True)
        for option in self.listing_options:
            self.add_option_field(option, False)

    def add_option_field(self, option, variation):
        """Add a product option field to the form."""
        name = f"option_{option.name}"
        self.fields[name] = fields.PartialProductOptionValueSelect(
            edit=self.edit, product_option=option
        )
        if variation is True:
            option_link = models.PartialProductRangeSelectedOption.objects.get(
                product_range=self.product_range, product_option=option
            )
            if option_link.pre_existing is True:
                self.fields[name].widget.attrs["disabled"] = True

    def clean(self):
        """Validate the form."""
        cleaned_data = super().clean()
        for option in self.options:
            name = f"option_{option.name}"
            if name not in cleaned_data or not cleaned_data[name]:
                cleaned_data[name] = ""
                self.add_error(
                    f"option_{option.name}", "Product option value cannot be empty."
                )
        return cleaned_data

    def variation(self):
        """Return a dict of submitted product option values."""
        variation = {}
        for option in self.variation_options:
            name = f"option_{option.name}"
            variation[name] = self.cleaned_data.get(name)
        return variation


class SetProductOptionValuesFormset(KwargFormSet):
    """Formset for adding values for a new product option to a range."""

    form = SetProductOptionValues

    def clean(self):
        """Validate the formset."""
        for form in self.forms:
            variation = form.variation()
            for otherform in (_ for _ in self.forms if _ != form):
                if variation == otherform.variation():
                    form.add_error(
                        None, "This variation is not unique within the Product Range."
                    )
        self.multiple_values_for_variation_options()
        return super().clean()

    def multiple_values_for_variation_options(self):
        """Add an error if a variation option only has one value."""
        variation = self.forms[0].variation()
        for key in variation.keys():
            if all(
                (form.variation().get(key) == variation[key] for form in self.forms)
            ):
                for form in self.forms:
                    form.add_error(
                        key,
                        "Every variation cannot have the same value for a drop down. "
                        "Should this be a listing option?",
                    )
                return

    @transaction.atomic
    def save(self):
        """Update the variation product options for a product range."""
        models.PartialProductOptionValueLink.objects.filter(
            product__product_range=self.forms[0].product_range
        ).delete()
        for form in self.forms:
            product = models.PartialProduct.objects.get(
                id=form.cleaned_data["product_ID"]
            )
            for option in form.options:
                models.PartialProductOptionValueLink(
                    product=product,
                    product_option_value=form.cleaned_data[f"option_{option.name}"],
                ).save()


class AddProductOptionValuesForm(forms.Form):
    """Form for adding product option values to a partial product edit."""

    def __init__(self, *args, **kwargs):
        """Add fields."""
        self.edit = kwargs.pop("edit")
        self.product_option = kwargs.pop("product_option")
        super().__init__(*args, **kwargs)
        self.fields[f"values"] = fields.VariationOptions(
            product_option=self.product_option,
            product_range=self.edit.partial_product_range,
            label=self.product_option.name,
        )

    def save(self):
        """Add product option values to the produt edit."""
        for value in self.cleaned_data["values"]:
            self.edit.product_option_values.add(value)
