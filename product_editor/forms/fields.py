"""Fields for use with forms for creating and editing products."""

import json
import re

from django import forms
from list_input import ListInput

from inventory import models
from product_editor.editor_manager import ProductEditorBase

from . import fieldtypes, widgets
from .fieldtypes import Validators


class Title(fieldtypes.TextField):
    """Product Range Title field."""

    label = "Title"
    name = "title"
    required_message = "Please supply a range title"
    placeholder = "Title"
    allowed_characters = ["%", "'"]
    help_text = (
        "The title for the product.<br>This applies to the "
        "Product Range and all of it's Products."
    )
    size = 60


class Description(fieldtypes.TextareaField):
    """Field for editing product descriptions."""

    required = False
    label = "Description"
    name = "description"
    html_class = "froala"
    placeholder = "Description. Will default to title if left blank"
    disallowed_characters = ["~"]
    help_text = (
        "The Description for the listings.<br>"
        "This can be changed on a channel by channel basis if necessary<br>"
        "If left blank the description will duplicate the title.<br>"
        "For variation items the description applies to the range as a whole."
    )

    def clean(self, value):
        """Remove invalid characters."""
        value = super().clean(value)
        value = value.replace("&nbsp;", " ")  # Remove Non breaking spaces
        value = re.sub(" +", " ", value)  # Remove multiple space characters
        return value


class Barcode(fieldtypes.TextField):
    """Field for product barcodes."""

    label = "Barcode"
    name = "barcode"
    placeholder = "Barcode"
    validators = [Validators.numeric]
    must_vary = True
    help_text = (
        "A unique barcode for the product.<br>"
        "If left blank one will be provided from stock."
    )


class VATRate(fieldtypes.SelectizeModelChoiceField):
    """Field for VAT rates."""

    label = "VAT Rate"
    name = "vat_rate"
    variable = True
    help_text = "The VAT rate that is applicable to the product."
    required_message = (
        "Please specify the appropriate <b>VAT Rate</b> for the " "product."
    )

    def get_queryset(self):
        """Return a queryset of selectable options."""
        return models.VATRate.objects.all()


class Price(fieldtypes.PriceField):
    """Field for product price."""

    label = "Price"
    name = "price"
    required_message = (
        "Please provide a <b>Price</b>. This cannot be blank but can be zero."
    )
    help_text = "The price at which the product is sold online."
    variable = True


class VATPrice(fieldtypes.CombinationField):
    """Combined field for VAT rate and price."""

    label = "Price"
    name = "vat_price"
    required = True
    required_message = "Please provide a <b>VAT rate</b> and <b>Price</b>."
    help_text = (
        "Please provide a <b>VAT rate</b> and <b>Price</b>.<br>"
        "The ex VAT price cannot be blank but can be zero."
    )

    def __init__(self, *args, **kwargs):
        """Create fields."""
        kwargs["label"] = "Price"
        fields = (
            forms.ChoiceField(
                required=True, choices=widgets.VATPriceWidget.vat_choices()
            ),
            forms.FloatField(required=True),
            forms.FloatField(required=True),
        )
        kwargs["widget"] = widgets.VATPriceWidget()
        super().__init__(fields=fields, require_all_fields=True, *args, **kwargs)

    def compress(self, data_list):
        """Return submitted values as a dict."""
        vat_rate, ex_vat_price, with_vat_price = data_list
        return {
            widgets.VATPriceWidget.VAT_RATE: vat_rate,
            widgets.VATPriceWidget.EX_VAT: ex_vat_price,
            widgets.VATPriceWidget.WITH_VAT_PRICE: with_vat_price,
        }


class PurchasePrice(fieldtypes.PriceField):
    """Field for purchase prices."""

    label = "Purchase Price"
    name = "purchase_price"
    required_message = (
        "Please provide a <b>Stock Level</b>. " "This cannot be blank but can be zero."
    )
    variable = True
    empty_value = 0.0
    help_text = (
        "Price at which we purchase the product." "<br>Cannot be blank but can be zero."
    )


class RetailPrice(fieldtypes.PriceField):
    """Field for retail prices."""

    label = "Retail Price"
    name = "retail_price"
    variable = True
    empty_value = 0.0
    help_text = "Price at which the item sold over the counter."


class StockLevel(fieldtypes.NumberField):
    """Field for stock level."""

    label = "Stock Level"
    name = "stock_level"
    initial = 0
    required_message = (
        "Please provide a stock level. This cannot be blank but can be zero."
    )
    variable = True
    empty_value = 0
    help_text = (
        "Initial <b>Stock Level</b> of the product."
        "<br>Cannot be blank but can be zero."
    )


class Supplier(fieldtypes.SelectizeModelChoiceField):
    """Field for selecting the supplier of a product."""

    label = "Supplier"
    name = "supplier"
    html_class = "selectize"
    required_message = (
        "A <b>Supplier</b> must be provided. If the supplier does appear in "
        "the list it must be added to Cloud Commerce before the product can be"
        " created."
    )
    help_text = (
        "The <b>Supplier</b> from which the product is purchased."
        "If the supplier does appear in the list it must be added to "
        "Cloud Commerce before the product can be created."
    )

    def get_queryset(self):
        """Return field choices."""
        return models.Supplier.objects.filter(inactive=False)


class SupplierSKU(fieldtypes.TextField):
    """Field for Supplier SKU."""

    label = "Supplier SKU"
    name = "supplier_SKU"
    placeholder = "Supplier SKU"
    variable = True
    help_text = "The <b>Supplier SKU</b> (Product Code) for the product."


class Weight(fieldtypes.NumberField):
    """Field for the weight of the product."""

    label = "Weight"
    name = "weight"
    required_message = "Please supply a weight. This cannot be blank but can be zero."
    variable = True
    empty_value = 0
    help_text = "The <b>Shipping Weight</b> of the product in <b>Grams</b>."


class Height(fieldtypes.NumberField):
    """Field for the height of the product."""

    label = "Height (Milimeters)"
    name = "height"
    variable = True
    empty_value = 0
    help_text = "The <b>Height</b> of the item when packed in <b>Milimeters</b>."


class Length(fieldtypes.NumberField):
    """Field for the length of the product."""

    label = "Length (Milimeters)"
    name = "length"
    variable = True
    empty_value = 0
    required = False
    help_text = "The <b>Length</b> of the item when packed in <b>Milimeters</b>."


class Width(fieldtypes.NumberField):
    """Field for the width of the product."""

    label = "Width (Milimeters)"
    name = "width"
    variable = True
    empty_value = 0
    help_text = "The <b>Width</b> of the item when packed in <b>Milimeters</b>."


class Dimensions(fieldtypes.CombinationField):
    """Combined field for height, width and lenght."""

    label = "Dimensions"
    help_text = "The dimensions of the product in <b>milimeters</b> when packed.<br>"

    def __init__(self, *args, **kwargs):
        """Create sub fields."""
        fields = (Height(), Width(), Length())
        kwargs["widget"] = widgets.DimensionsWidget()
        super().__init__(
            *args, fields=fields, require_all_fields=False, required=False, **kwargs
        )

    def compress(self, value):
        """Return submitted values as a dict."""
        if not value:
            value = [0, 0, 0]
        return {"height": value[0], "length": value[1], "width": value[2]}


class PackageType(fieldtypes.SelectizeModelChoiceField):
    """Field for selecting the package type of a product."""

    label = "Package Type"
    name = "package_type"
    variable = True
    required_message = "A <b>Package Type</b> must be supplied."
    help_text = (
        "The <b>Shipping Rule</b> will be selected acording to the "
        "<b>Package Type</b>."
    )
    selectize_options = {"maxItems": 1}

    def get_queryset(self):
        """Return a queryset of selectable options."""
        return models.PackageType.objects.filter(inactive=False)


class InternationalShipping(fieldtypes.SelectizeModelChoiceField):
    """Field for selecting the International Shipping class of a product."""

    label = "International Shipping"
    name = "international_shipping"
    variable = True
    required_message = "An <b>International Shipping type</b> must be supplied."
    help_text = (
        "The <b>Shipping Rule</b> will be selected acording to the "
        "<b>International Shipping type</b>."
    )
    selectize_options = {"maxItems": 1}

    def get_queryset(self):
        """Return a queryset of selectable options."""
        return models.InternationalShipping.objects.filter(inactive=False)


class Department(fieldtypes.SelectizeModelChoiceField):
    """Field for product department."""

    label = "Department"
    name = "department"
    required_message = "A <b>Department</b> must be selected."
    help_text = "The <b>Department</b> to which the product belongs."

    def get_queryset(self):
        """Return a queryset of selectable options."""
        return models.Department.objects.filter(inactive=False)


class Warehouse(fieldtypes.SingleSelectize):
    """Field for product department."""

    label = "Department"
    name = "department"
    required_message = "A <b>Department</b> must be selected."
    help_text = "The <b>Department</b> to which the product belongs."

    def __init__(self, *args, **kwargs):
        """Initialise field."""
        kwargs["choices"] = self.get_choices()
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_choices():
        """Get choice options for field."""
        departments = [
            (w.warehouse_ID, w.name) for w in models.Warehouse.used_warehouses.all()
        ]
        departments.sort(key=lambda x: x[1])
        return [("", "")] + departments

    def clean(self, value):
        """Validate cleaned data."""
        value = super().clean(value)
        if self.required is False and value == "":
            return None
        try:
            department = models.Warehouse.used_warehouses.get(
                warehouse_ID=int(value)
            ).warehouse_ID
        except models.Warehouse.DoesNotExist:
            raise forms.ValidationError("Deparment not recognised")
        return department


class Location(fieldtypes.SelectizeField):
    """Field for choosing warehouse bays."""

    label = "Location"
    name = "location"
    placeholder = "Location"
    variable = True
    html_class = "location_field"
    required = False
    help_text = (
        "The name of the <b>Bay</b> in which the product will be located."
        "<br>This should be left blank if the product does not have a "
        "specific <b>Bay</b>.<br>If additional bays are required they "
        "must be added after the product has been created."
    )
    selectize_options = {
        "delimiter": ",",
        "persist": False,
        "maxItems": None,
        "sortField": "text",
    }

    def __init__(self, **kwargs):
        """Set department."""
        self.warehouse = kwargs.get("department")
        super().__init__(required=kwargs.get("required"), choices=self.get_choices())

    def get_choices(self):
        """Return choices for field."""
        if self.warehouse is None:
            warehouses = models.Warehouse.used_warehouses.all()
            options = [["", ""]]
            for warehouse in warehouses:
                options.append(
                    [
                        warehouse.name,
                        [[bay.bay_ID, bay] for bay in warehouse.bay_set.all()],
                    ]
                )
            return options
        else:
            try:
                warehouse = self.get_warehouse()
            except models.Warehouse.DoesNotExist:
                return [("", "")]
            else:
                return [(bay.bay_ID, bay.name) for bay in warehouse.bay_set.all()]

    def get_warehouse(self):
        """Return Warehouse object matching the field's warehouse."""
        if isinstance(self.warehouse, int):
            return models.Warehouse.objects.get(warehouse_ID=self.warehouse)
        return models.Warehouse.objects.get(name=self.warehouse)

    def to_python(self, *args, **kwargs):
        """Return submitted bays as a list of bay IDs."""
        return [int(x) for x in super().to_python(*args, **kwargs)]

    def get_bay_objects(self, value):
        """Return the subbmitted bays as a list of Bay model objects."""
        bays = []
        for bay_ID in value:
            try:
                bays.append(models.Bay.objects.get(bay_ID=bay_ID))
            except models.DoesNotExist:
                raise forms.ValidationError("Bay not recognised")
        return bays

    def check_warehouse(self, bays):
        """Return the warehouse to which the bays belong or raise ValidationError."""
        if self.warehouse is None and not bays:
            raise forms.ValidationError("At least one bay must be provided.")
            return
        warehouse = self.warehouse or bays[0].warehouse
        if not all((bay.warehouse == warehouse for bay in bays)):
            raise forms.ValidationError("All bays must be in the same warehouse.")
        return warehouse

    def clean(self, value):
        """Validate bay selection."""
        value = super().clean(value)
        bays = self.get_bay_objects(value)
        warehouse = self.check_warehouse(bays)
        primary_bays = [bay for bay in bays if bay.is_primary]
        if primary_bays:
            bays = [bay for bay in bays if not bay.is_default]
        else:
            if warehouse and not any((bay.is_default for bay in bays)):
                bays.append(warehouse.default_bay)
        value = [b.bay_ID for b in bays]
        return value


class WarehouseBayField(fieldtypes.CombinationField):
    """Combined Department and Location fields."""

    label = "Location"
    help_text = (
        "Select the <b>Warehouse</b> from which the item will be picked.<br>"
        "Bays in this Warehouse can then be added to the Bay field."
        "<br>If the bay field is left blank the default bay for the Warehouse"
        " will be added."
    )

    WAREHOUSE = ProductEditorBase.WAREHOUSE
    BAYS = ProductEditorBase.BAYS

    def __init__(self, *args, **kwargs):
        """Create sub fields."""
        kwargs["label"] = "Location"
        self.lock_warehouse = kwargs.pop("lock_warehouse", False)
        fields = (Warehouse(), Location(required=False))
        selectize_options = [field.selectize_options for field in fields]
        if self.lock_warehouse:
            selectize_options[0]["readOnly"] = True
        warehouse_choices = fields[0].get_choices()
        location_choices = fields[1].get_choices()
        kwargs["widget"] = widgets.WarehouseBayWidget(
            choices=[warehouse_choices, location_choices],
            selectize_options=selectize_options,
            lock_warehouse=self.lock_warehouse,
            inline=kwargs.pop("inline", False),
        )
        super().__init__(fields=fields, require_all_fields=False, *args, **kwargs)

    def compress(self, value):
        """Return submitted values as a dict."""
        return {self.WAREHOUSE: value[0], self.BAYS: value[1]}

    def clean(self, value):
        """Validate submitted values."""
        value = super().clean(value)
        warehouse = models.Warehouse.objects.get(warehouse_ID=value[self.WAREHOUSE])
        bays = models.Bay.objects.filter(bay_ID__in=value[self.BAYS], is_default=False)
        if not all((bay.warehouse == bays[0].warehouse for bay in bays)):
            raise Exception("FIX THIS")
        value[self.WAREHOUSE] = warehouse.warehouse_ID
        if len(bays) == 0:
            bays = [warehouse.default_bay]
        cleaned_value = {
            self.WAREHOUSE: warehouse.warehouse_ID,
            self.BAYS: [bay.bay_ID for bay in bays],
        }
        return cleaned_value


class ProductOptionValueField(fieldtypes.SelectizeField):
    """Base field class for editing Product Options."""

    option_allowed_characters = {
        "Size": ["+", "-", ".", "/", "'", '"', "(", ")"],
        "Weight": ["."],
        "Strength": ["+", "-", "."],
        "Material": ["%", ","],
    }

    def __init__(self, *args, **kwargs):
        """Set options for selectize."""
        self.product_option = kwargs.pop("product_option")
        self.product_range = kwargs.pop("product_range", None)
        kwargs["choices"] = self.get_choices()
        self.selectize_options = self.selectize_options.copy()
        self.selectize_options["create"] = True
        self.allowed_characters = self.option_allowed_characters.get(
            self.product_option.name
        )
        super().__init__(*args, **kwargs)

    def get_choices(self):
        """Return the choices for the field."""
        choices = [("", "")]
        available_options = models.ProductOptionValue.objects.filter(
            product_option=self.product_option
        )
        if self.product_range is not None:
            available_options = self.remove_used_options(
                available_options, self.product_range
            )
        choices += [(option.value, option.value) for option in available_options]
        return choices

    def remove_used_options(self, available_options, product_range):
        """Filter values already used by the product from the choices."""
        existing_links = models.PartialProductOptionValueLink.objects.filter(
            product__product_range=self.product_range,
            product_option_value__product_option=self.product_option,
        )
        existing_values = models.ProductOptionValue.objects.filter(
            id__in=existing_links.values_list("product_option_value__id", flat=True)
        )
        return available_options.difference(existing_values)

    def valid_value(self, value):
        """Allow values not in choices."""
        return True

    def validate(self, values):
        """Validate each input value."""
        if self.allowed_characters is not None:
            for value in values:
                Validators.allow_characters(value, self.allowed_characters)

    def clean(self, values):
        """
        Return the values as model objects.

        Create an non-existant values.
        """
        options = []
        for value in values:
            try:
                option = models.ProductOptionValue.objects.get(
                    product_option=self.product_option, value=value
                )
            except models.ProductOptionValue.DoesNotExist:
                raise NotImplementedError(
                    "Creating new product options is not implemented."
                )
            options.append(option)
        return options


class VariationOptions(ProductOptionValueField):
    """Field for Product Options that define variations."""

    pass


class ListingOption(ProductOptionValueField):
    """Field for options that provide information for listings."""

    pass


class PartialProductOptionValueSelect(fieldtypes.SelectizeModelChoiceField):
    """Select a product option value for a parital product."""

    def __init__(self, *args, **kwargs):
        """Select a product option value for a parital product."""
        self.edit = kwargs.pop("edit")
        self.product_option = kwargs.pop("product_option")
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        """Return the name of the option as it should appear in the form."""
        return obj.value

    def get_queryset(self):
        """Return a queryset of selectable options."""
        return self.edit.product_option_values.filter(
            product_option=self.product_option
        )


class Brand(fieldtypes.SelectizeModelChoiceField):
    """Field for product department."""

    label = "Brand"
    name = "brand"
    required_message = "Please supply a brand"
    help_text = "The <b>Brand</b> of the product.<br>This is required for listings."

    def get_queryset(self):
        """Return a queryset of selectable options."""
        return models.Brand.objects.filter(inactive=False)


class Manufacturer(fieldtypes.SelectizeModelChoiceField):
    """Field for the manufacturer of the product."""

    label = "Manufacturer"
    name = "manufacturer"
    required_message = ("Please supply a manufacturer",)
    placeholder = "Manufacturer"
    help_text = (
        "The <b>Manufacturer</b> of the product.<br>This is required for " "listings."
    )

    def get_queryset(self):
        """Return a queryset of selectable options."""
        return models.Manufacturer.objects.filter(inactive=False)


class Gender(fieldtypes.SelectizeModelChoiceField):
    """Field for the gender option of Amazon listings."""

    label = "Gender"
    name = "gender"
    placeholder = "Gender"
    variable = True
    help_text = "Gender for which the product is intended."

    def get_queryset(self):
        """Return a queryset of selectable options."""
        return models.Gender.objects.all()


class ListOption(fieldtypes.FormField, ListInput):
    """Base class for fields based on ListInput."""

    separator = "|"
    disallowed_characters = [separator]

    def clean(self, value):
        """Clean submitted value."""
        if value is None:
            return []
        value = json.loads(value)
        return value


class AmazonBulletPoints(ListOption):
    """Field for Amazon bullet point descriptions."""

    label = "Amazon Bullet Points"
    name = "amazon_bullet_points"
    html_class = "amazon_bullet_points"
    help_text = "Create upto five bullet points for Amazon listings."
    maximum = 5


class AmazonSearchTerms(ListOption):
    """Field for Amazon search terms."""

    label = "Amazon Search Terms"
    name = "amazon_search_terms"
    html_class = "amazon_search_terms"
    help_text = "Create upto five search terms for Amazon listings."
    maximum = 5


class SelectProductOption(fieldtypes.SelectizeModelChoiceField):
    """Field for selecting the package type of a product."""

    label = "Product Option"
    name = "product_option"
    required_message = "A <b>Package Type</b> must be supplied."
    help_text = (
        "The <b>Shipping Rule</b> will be selected acording to the "
        "<b>Package Type</b>."
    )
    selectize_options = {"maxItems": 1}

    def __init__(self, *args, **kwargs):
        """Instanciate the field."""
        self.product_range = kwargs.pop("product_range", None)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        """Return a queryset of selectable options."""
        queryset = models.ProductOption.objects.filter(inactive=False)
        if self.product_range is not None:
            selected_options = self.product_range.product_options.values_list(
                "pk", flat=True
            )
            queryset = queryset.exclude(pk__in=selected_options)
        return queryset
