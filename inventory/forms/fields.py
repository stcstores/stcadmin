"""Fields for use with forms for creating and editing products."""

import re

from django import forms

from inventory import models

from . import fieldtypes, widgets
from .fieldtypes import Validators


class BayField(forms.ModelMultipleChoiceField):
    """Field for selecting bays."""

    widget = widgets.MultipleBayWidget(attrs={"data-minimum-input-length": 1})


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
    size = 60


class Description(fieldtypes.TextareaField):
    """Field for editing product descriptions."""

    required = False
    label = "Description"
    name = "description"
    html_class = "froala"
    placeholder = "Description. Will default to title if left blank"
    disallowed_characters = ["~"]

    def clean(self, value):
        """Remove invalid characters."""
        value = super().clean(value)
        value = value.replace("&nbsp;", " ")  # Remove Non breaking spaces
        value = re.sub(" +", " ", value)  # Remove multiple space characters
        return value


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
        choices += [(option, option) for option in available_options]
        return choices

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
