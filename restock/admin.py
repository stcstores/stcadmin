"""Model Admin for the restock app."""

from django.contrib import admin

from restock import models


@admin.register(models.Reorder)
class ReorderAdmin(admin.ModelAdmin):
    """Model admin for the Reorder model."""

    exclude_fields = ()
    list_display = ("product", "count", "comment")
    list_editable = ("count", "comment")
    search_fields = (
        "product__sku",
        "product__id",
        "product__product_range__sku",
        "product__product_range__id",
        "product__supplier",
    )
    list_filter = ("product__supplier",)
    list_select_related = ("product__supplier", "product__product_range")
