"""Fields for use with forms for creating and editing products."""

import re

from django import forms

from inventory import models

from . import fieldtypes, widgets
from .fieldtypes import Validators


class Brand(forms.ModelChoiceField):
    """Field for product brand."""

    required_message = "Please supply a brand"
    help_text = "The <b>Brand</b> of the product.<br>This is required for listings."
    widget = widgets.BrandWidget


class Manufacturer(forms.ModelChoiceField):
    """Field for product manufacturer."""

    required_message = ("Please supply a manufacturer",)
    help_text = (
        "The <b>Manufacturer</b> of the product.<br>This is required for " "listings."
    )
    widget = widgets.ManufacturerWidget


class Supplier(forms.ModelChoiceField):
    """Field for product supplier."""

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
    widget = widgets.SupplierWidget


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


class VATRateField(fieldtypes.SelectizeModelChoiceField):
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


class HSCode(fieldtypes.TextField):
    """Field for product HS Codes."""

    label = "HS Code"
    name = "hs_code"
    placeholder = "HS Code"
    validators = [Validators.numeric]
    required_message = "Please provide an HS Code"
    variable = True
    help_text = "The product's HS Code"
    widget = widgets.HSCodeWidget()


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
            *args, fields=fields, require_all_fields=True, required=True, **kwargs
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
        return models.PackageType.objects.filter(active=True)


class BayField(fieldtypes.SelectizeModelMultipleChoiceField):
    """Field for choosing warehouse bays."""

    label = "Bays"
    name = "bays"
    placeholder = "Bays"
    variable = True
    html_class = "location_field"
    required = False
    help_text = (
        "The name of the <b>Bay</b> in which the product will be located."
        "<br>This should be left blank if the product does not have a "
        "specific <b>Bay</b>.<br>If additional bays are required they "
        "must be added after the product has been created."
    )

    def get_queryset(self):
        """Return choices for field."""
        return models.Bay.objects.filter(active=True)


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
        self.variation_option = kwargs.pop("variation_option")
        self.product_range = kwargs.pop("product_range", None)
        self.selectize_options = self.selectize_options.copy()
        self.selectize_options["create"] = True
        self.allowed_characters = self.option_allowed_characters.get(
            self.variation_option.name
        )
        super().__init__(*args, **kwargs)

    def get_choices(self):
        """Return the choices for the field."""
        choices = [("", "")]
        available_options = (
            models.VariationOptionValue.objects.filter(
                variation_option=self.variation_option
            )
            .values_list("value", flat=True)
            .distinct()
        )
        if self.product_range is not None:
            available_options = self.remove_used_options(
                available_options, self.product_range
            )
        choices += [(option, option) for option in available_options]
        return choices

    def remove_used_options(self, available_options, product_range):
        """Filter values already used by the product from the choices."""
        existing_links = (
            models.VariationOptionValue.objects.filter(
                product__product_range=self.product_range,
            )
            .values_list("variation_option", flat=True)
            .distinct()
            .order_by()
        )
        existing_values = models.VariationOption.objects.filter(
            id__in=existing_links.values_list("name", flat=True)
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


class VariationOptions(ProductOptionValueField):
    """Field for Product Options that define variations."""

    pass


class ListingOption(ProductOptionValueField):
    """Field for options that provide information for listings."""

    pass


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
        queryset = models.ProductOption.objects.filter(active=True)
        if self.product_range is not None:
            selected_options = self.product_range.product_options.values_list(
                "pk", flat=True
            )
            queryset = queryset.exclude(pk__in=selected_options)
        return queryset
