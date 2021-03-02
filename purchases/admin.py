"""Model admin for the Purchases app."""

from django.contrib import admin
from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)

from purchases import models


class PurchaseChildAdmin(PolymorphicChildModelAdmin):
    """Model Admin for children of purchases.models.Purchase."""

    base_fields = ("user", "to_pay")


@admin.register(models.StockPurchase)
class StockPurchaseAdmin(PurchaseChildAdmin):
    """Model admin for the StockPurchase mode."""

    base_model = models.Purchase


@admin.register(models.ShippingPurchase)
class ShippingPurchaseAdmin(PurchaseChildAdmin):
    """Model admin for the ShippingPurchase mode."""

    base_model = models.Purchase


@admin.register(models.Purchase)
class PurchasesAdmin(PolymorphicParentModelAdmin):
    """ModelAdmin for the Purchases model."""

    base_model = models.Purchase
    child_models = (models.StockPurchase, models.ShippingPurchase)
    list_filter = (PolymorphicChildModelFilter,)
