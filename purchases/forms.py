"""Forms for the purchases app."""

import logging

from django import forms
from django.db.models import Q

from home.models import Staff
from inventory.models import BaseProduct
from linnworks.models import StockManager
from purchases import models


class ProductSearchForm(forms.Form):
    """Form for searching for products to purchase."""

    search_term = forms.CharField(required=False)

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
        self.instance = models.Purchase.objects.new_purchase(
            purchased_by=self.cleaned_data["purchaser"],
            product=product,
            quantity=self.cleaned_data["quantity"],
        )

    def update_stock_level(self):
        """Update the stock level of a product to reflect the created purchase."""
        try:
            current_stock_level = StockManager.get_stock_level(self.instance.product)
            new_stock_level = current_stock_level - self.instance.quantity
            if new_stock_level < 0:
                raise Exception("Cannot set stock level below zero.")
            updated_stock_level = StockManager.set_stock_level(
                product=self.instance.product,
                user=self.instance.purchased_by.stcadmin_user,
                new_stock_level=new_stock_level,
                change_source="Staff purchase by {{ purchase.purchased_by }}",
            )
        except Exception as e:
            logger = logging.getLogger("django")
            logger.exception(e)
            raise
        else:
            return updated_stock_level
