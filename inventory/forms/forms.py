"""Forms for inventory app."""

import json

from django import forms
from django_summernote.widgets import SummernoteInplaceWidget

from inventory import models
from inventory.forms import fields as inventory_fields
from stcadmin.forms import KwargFormSet, MultipleFileInput, MultipleImageField


class ListWidget(forms.TextInput):
    """Widget for search terms and bullet point inputs."""

    template_name = "inventory/widgets/list_widget.html"


class BaseRangeForm(forms.ModelForm):
    """Base form for editing product ranges."""

    class Meta:
        """Meta for RangeForm."""

        model = models.ProductRange
        exclude = ["hidden", "status", "images", "search_terms", "bullet_points"]
        field_classes = {"name": inventory_fields.Title}
        widgets = {"description": SummernoteInplaceWidget}


class CreateRangeForm(BaseRangeForm):
    """Form for editing attributes that are the same across a range."""

    class Meta(BaseRangeForm.Meta):
        """Meta for CreateRangeForm."""

        widgets = BaseRangeForm.Meta.widgets | {"managed_by": forms.HiddenInput}

    sku = forms.CharField(required=False, widget=forms.HiddenInput)


class EditRangeForm(BaseRangeForm):
    """Form for editing attributes that are the same across a range."""

    class Meta(BaseRangeForm.Meta):
        """Meta for CreateRangeForm."""

        exclude = BaseRangeForm.Meta.exclude + ["sku"]

    field_order = ("name", "description", "managed_by")


class BaseProductForm(forms.ModelForm):
    """Form for editing indivdual Products."""

    class Meta:
        """Meta for BaseProductForm."""

        model = models.Product
        exclude = (
            "is_end_of_line",
            "end_of_line_reason",
            "gender",
            "range_order",
            "images",
            "is_archived",
            "is_end_of_line",
        )
        field_classes = {
            "brand": inventory_fields.Brand,
            "manufacturer": inventory_fields.Manufacturer,
            "supplier": inventory_fields.Supplier,
            "additional_suppliers": inventory_fields.AdditionalSuppliers,
        }

    field_order = (
        "supplier_barcode",
        "barcode",
        "purchase_price",
        "vat_rate",
        "supplier",
        "additional_suppliers",
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
        "bays",
        "is_flammable",
    )

    def __init__(self, *args, **kwargs):
        """Set packing requirements field size attribute."""
        super().__init__(*args, **kwargs)
        self.fields["packing_requirements"].widget.attrs.update(
            {"size": models.PackingRequirement.objects.count()}
        )


class InitialVariationForm(BaseProductForm):
    """Form for setting initial product attributes."""

    SINGLE = "single"
    VARIATION = "variation"

    class Meta(BaseProductForm.Meta):
        """Meta for InitialProductForm."""

        model = models.InitialVariation
        widgets = {"product_range": forms.HiddenInput, "sku": forms.HiddenInput}
        exclude = BaseProductForm.Meta.exclude + (
            "bays",
            "additional_suppliers",
        )

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

    bays = inventory_fields.BayField(
        queryset=models.Bay.objects.filter(active=True), required=False
    )

    class Meta(BaseProductForm.Meta):
        """Meta class for EditProductForm."""

        exclude = BaseProductForm.Meta.exclude + ("product_range", "sku")

    def __init__(self, *args, **kwargs):
        """Allow user to be passed to the form."""
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def get_initial_for_field(self, field, field_name):
        """Set the initial value for the bays field."""
        if field_name == "bays":
            return models.Bay.objects.get_bays_for_product(self.instance)
        return super().get_initial_for_field(field, field_name)

    def save(self, *args, **kwargs):
        """Update the product."""
        obj = super().save(*args, **kwargs)
        models.ProductBayHistory.objects.set_product_bays(
            user=self.user,
            product=obj,
            bays=self.cleaned_data["bays"],
        )
        return obj


class ProductFormset(KwargFormSet):
    """Formset for updating the locations of all Products within a Range."""

    form = EditProductForm


class SetupVariationsForm(forms.Form):
    """Setup variaion product options for a new product."""

    variations = forms.CharField(
        error_messages={"required": "Variation options cannot be empty."},
        widget=forms.TextInput(attrs={"class": "invisble"}),
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


class AddSupplierToBlacklistForm(forms.Form):
    """Form for adding blacklisted suppliers."""

    name = forms.CharField()

    def save(self):
        """Set an existing supplier as blacklisted or create a new one."""
        self.instance, _ = models.Supplier.objects.update_or_create(
            name=self.cleaned_data["name"], defaults={"blacklisted": True}
        )
        return self.instance


class EndOfLineReasonForm(forms.Form):
    """Form for setting products as end of line."""

    end_of_line_reason = forms.ModelChoiceField(
        models.EndOfLineReason.objects.all(), required=True
    )
