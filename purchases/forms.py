"""Forms for the purchases app."""

from django import forms
from django.db.models import Q

from home.models import Staff
from inventory.models import BaseProduct
from purchases import models


class ProductSearchForm(forms.Form):
    """Form for searching for products to purchase."""

    search_term = forms.CharField()

    def get_queryset(self):
        """Return a queryset of matching products."""
        if self.is_valid():
            search_term = self.cleaned_data["search_term"]
            return (
                BaseProduct.objects.complete()
                .active()
                .filter(
                    Q(sku=search_term)
                    | Q(supplier_sku=search_term)
                    | Q(barcode=search_term)
                    | Q(product__product_range__name__icontains=search_term)
                    | Q(product__product_range__sku=search_term)
                )
                .distinct()
                .select_related("product_range")
            )
        raise Exception("Form is invalid")


class CreatePurchaseForm(forms.Form):
    """Form for creating purchases."""

    purchaser = forms.ModelChoiceField(queryset=Staff.unhidden.all())
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField()

    def save(self):
        """Create a new purchase."""
        product = BaseProduct.objects.get(pk=self.cleaned_data["product_id"])
        models.Purchase.objects.new_purchase(
            purchased_by=self.cleaned_data["purchaser"],
            product=product,
            quantity=self.cleaned_data["quantity"],
        )
