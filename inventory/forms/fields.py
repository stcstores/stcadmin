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


class ListingOption(ProductOptionValueField):
    """Field for options that provide information for listings."""
