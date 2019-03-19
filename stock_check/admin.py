"""Model Admin for Stock Check app."""

from django.contrib import admin

from stock_check import models


@admin.register(models.StockCheckProduct)
class StockCheckProductAdmin(admin.ModelAdmin):
    """Model admin for the StockCheckProduct model."""

    fields = ("range_id", "product_id", "sku")
    list_display = ("__str__", "range_id", "product_id", "sku", "bay_names")
    list_display_links = ("__str__",)
    list_editable = ("range_id", "product_id", "sku")
    search_fields = ("range_id", "product_id", "sku")


@admin.register(models.ProductBay)
class ProductBayAdmin(admin.ModelAdmin):
    """Model admin for the Product Bay model."""

    fields = ("product", "bay", "stock_level")
    list_display = ("product", "bay", "stock_level")
