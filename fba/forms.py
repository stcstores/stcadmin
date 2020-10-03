"""Forms for the FBA app."""

from ccapi import CCAPI
from django import forms

from fba import models


class SelectFBAOrderProduct(forms.Form):
    """Form for selecting a product for an FBA order."""

    product_SKU = forms.CharField()

    def clean(self):
        """Add product ID to cleaned data."""
        cleaned_data = super().clean()
        try:
            search_result = CCAPI.search_products(cleaned_data["product_SKU"])
            if len(search_result) > 1:
                self.add_error("Too many products found")
            else:
                product = search_result[0]
            cleaned_data["product_ID"] = product.variation_id
        except Exception:
            self.add_error("Product not found")


class CreateFBAOrderForm(forms.ModelForm):
    """Form for creating FBA orders."""

    def __init__(self, *args, **kwargs):
        """Disable non-editable fields."""
        super().__init__(*args, **kwargs)
        self.fields["product_SKU"].disabled = True
        self.fields["product_ID"].disabled = True
        self.fields["product_name"].disabled = True

    class Meta:
        """Meta class for CreateFBAOrderForm."""

        model = models.FBAOrder
        fields = [
            "country",
            "product_SKU",
            "product_ID",
            "product_name",
            "selling_price",
            "FBA_fee",
            "aproximate_quantity",
            "notes",
        ]
        widgets = {"product_ID": forms.HiddenInput()}


class FBAOrderFilter(forms.Form):
    """Form for filtering the FBA order list."""

    def query_kwargs(self, data):
        """Return a dict of filter kwargs."""
        return {}

    def get_queryset(self):
        """Return a queryset of orders based on the submitted data."""
        kwargs = self.query_kwargs(self.cleaned_data)
        qs = models.FBAOrder.objects.filter(**kwargs)
        return qs