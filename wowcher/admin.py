"""ModelAdmin classes for the wowcher app."""

from django.contrib import admin
from wowcher import models


@admin.register(models.WowcherDeal)
class WowcherDealAdmin(admin.ModelAdmin):
    """ModelAdmin for the WowcherDeal model."""

    fields = (
        "deal_id",
        "name",
        "product_SKU",
        "product_ID",
        "item_net",
        "item_gross",
        "total_net",
        "total_gross",
    )
    list_display = (
        "__str__",
        "deal_id",
        "name",
        "product_SKU",
        "product_ID",
        "item_net",
        "item_gross",
        "total_net",
        "total_gross",
        "created",
        "ended",
        "inactive",
    )
    list_display_links = ("__str__",)
    list_editable = (
        "deal_id",
        "name",
        "product_SKU",
        "product_ID",
        "item_net",
        "item_gross",
        "total_net",
        "total_gross",
    )
    list_filter = ("inactive",)
    search_fields = ("deal_id", "name", "product_SKU")


@admin.register(models.WowcherOrder)
class WowcherOrderAdmin(admin.ModelAdmin):
    """ModelAdmin for the WowcherOrder model."""

    fields = ("deal", "wowcher_code", "cloud_commerce_order_ID", "status", "canceled")
    list_display = (
        "__str__",
        "deal",
        "wowcher_code",
        "cloud_commerce_order_ID",
        "status",
        "canceled",
    )
    list_display_links = ("__str__",)
    list_editable = ("wowcher_code", "cloud_commerce_order_ID", "status", "canceled")
    search_fields = (
        "deal__deal_id",
        "deal__name",
        "deal__product_SKU",
        "cloud_commerce_order_ID",
    )
