"""Model admin for Suppliers app."""

from django.contrib import admin
from suppliers import models


@admin.register(models.Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Model admin for the Supplier model."""

    list_display = ("name", "email", "phone")


@admin.register(models.StockItem)
class StockItemAdmin(admin.ModelAdmin):
    """Model admin for the StockItem model."""

    list_display = (
        "product_code",
        "supplier_title",
        "box_quantity",
        "linnworks_title",
        "linnworks_sku",
        "supplier",
    )
