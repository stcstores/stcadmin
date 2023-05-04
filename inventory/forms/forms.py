"""Forms for inventory app."""


import json

from django import forms
from django.contrib.postgres.forms import SplitArrayField

from inventory import models
from inventory.forms import fields as inventory_fields
from stcadmin.forms import KwargFormSet, MultipleFileInput, MultipleImageField


class BaseRangeForm(forms.ModelForm):
    """Base form for editing product ranges."""

    class Meta:
        """Meta for RangeForm."""

        model = models.ProductRange
        exclude = ["hidden", "status", "images"]
        field_classes = {
            "name": inventory_fields.Title,
            "description": inventory_fields.Description,
        }

    search_terms = SplitArrayField(
        forms.CharField(), size=5, required=False, remove_trailing_nulls=True
    )
    bullet_points = SplitArrayField(
        forms.CharField(), size=5, required=False, remove_trailing_nulls=True
    )


class CreateRangeForm(BaseRangeForm):
    """Form for editing attributes that are the same across a range."""

    class Meta(BaseRangeForm.Meta):
        """Meta for CreateRangeForm."""

        exclude = BaseRangeForm.Meta.exclude + ["is_end_of_line"]
        widgets = {"managed_by": forms.HiddenInput}

    sku = forms.CharField(required=False, widget=forms.HiddenInput)


class EditRangeForm(BaseRangeForm):
    """Form for editing attributes that are the same across a range."""

    class Meta(BaseRangeForm.Meta):
        """Meta for CreateRangeForm."""

        exclude = BaseRangeForm.Meta.exclude + ["sku"]

    field_order = ("name", "description", "managed_by", "is_end_of_line")


class BaseProductForm(forms.ModelForm):
    """Form for editing indivdual Products."""

    class Meta:
        """Meta for BaseProductForm."""

        model = models.Product
        exclude = (
            "is_end_of_line",
            "gender",
            "range_order",
            "images",
        )
        field_classes = {
            "brand": inventory_fields.Brand,
            "manufacturer": inventory_fields.Manufacturer,
            "supplier": inventory_fields.Supplier,
        }

    field_order = (
        "supplier_barcode",
        "barcode",
        "purchase_price",
        "vat_rate",
        "supplier",
        "supplier_sku",
        "brand",
        "manufacturer",
        "dimensions",
        "package_type",
        "hs_code",
        "weight_grams",
        "width",
        "height",
        "depth",
        "retail_price",
    )


class InitialVariationForm(BaseProductForm):
    """Form for setting initial product attributes."""

    SINGLE = "single"
    VARIATION = "variation"

    class Meta(BaseProductForm.Meta):
        """Meta for InitialProductForm."""

        model = models.InitialVariation
        widgets = {"product_range": forms.HiddenInput, "sku": forms.HiddenInput}

    sku = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self, *args, **kwargs):
        """Return cleaned form data."""
        cleaned_data = super().clean(*args, **kwargs)
        cleaned_data["sku"] = models.new_product_sku()
        if self.data["product_type"] == self.SINGLE:
            self.instance.__class__ = models.Product
        return cleaned_data


class EditProductForm(BaseProductForm):
    """Form for editing the Product model."""

    class Meta(BaseProductForm.Meta):
        """Meta class for EditProductForm."""

        exclude = BaseProductForm.Meta.exclude + ("product_range", "sku")


class ProductFormset(KwargFormSet):
    """Formset for updating the locations of all Products within a Range."""

    form = EditProductForm


class SetupVariationsForm(forms.Form):
    """Setup variaion product options for a new product."""

    variations = forms.CharField(
        error_messages={"required": "Variation options cannot be empty."},
    )

    def __init__(self, *args, **kwargs):
        """Add fields."""
        super().__init__(*args, **kwargs)
        for variation_option in models.VariationOption.objects.all():
            self.fields[str(variation_option.pk)] = inventory_fields.VariationOptions(
                required=False,
                variation_option=variation_option,
                label=variation_option.name,
            )


class ImagesForm(forms.Form):
    """Form for adding product images."""

    product_ids = forms.CharField(widget=forms.HiddenInput)
    images = MultipleImageField(
        required=False,
        label="Images",
        widget=MultipleFileInput(attrs={"multiple": True, "accept": ".jpg, .png"}),
    )

    def clean(self):
        """Get products to add images to."""
        cleaned_data = super().clean()
        product_ids = json.loads(cleaned_data["product_ids"])
        cleaned_data["products"] = models.BaseProduct.objects.filter(
            pk__in=product_ids
        ).prefetch_related("images")
        return cleaned_data
