"""ModelAdmin classes for the wowcher app."""

from django.contrib import admin

from wowcher import models


@admin.register(models.WowcherDeal)
class WowcherDealAdmin(admin.ModelAdmin):
    """ModelAdmin for the WowcherDeal model."""

    fields = ("deal_ID", "name", "shipping_price", "ended", "inactive")
    list_display = (
        "__str__",
        "deal_ID",
        "name",
        "shipping_price",
        "created",
        "stock_alert_level",
        "ended",
        "inactive",
    )
    list_display_links = ("__str__",)
    list_editable = (
        "deal_ID",
        "name",
        "shipping_price",
        "ended",
        "inactive",
        "stock_alert_level",
    )
    list_filter = ("inactive",)
    search_fields = ("deal_ID", "name")


@admin.register(models.WowcherItem)
class WowcherItemAdmin(admin.ModelAdmin):
    """ModelAdmin for the WowcherItem model."""

    fields = ("deal", "wowcher_ID", "CC_SKU", "CC_product_ID")
    list_display = (
        "__str__",
        "deal",
        "wowcher_ID",
        "CC_SKU",
        "CC_product_ID",
        "hide_stock_alert",
    )
    list_display_links = ("__str__",)
    list_editable = (
        "deal",
        "wowcher_ID",
        "CC_SKU",
        "CC_product_ID",
        "hide_stock_alert",
    )
    search_fields = (
        "deal__deal_ID",
        "deal__name",
        "wowcher_ID",
        "CC_SKU",
        "CC_product_ID",
    )


@admin.register(models.WowcherOrder)
class WowcherOrderAdmin(admin.ModelAdmin):
    """ModelAdmin for the WowcherOrder model."""

    fields = (
        "deal",
        "wowcher_code",
        "customer_name",
        "CC_order_ID",
        "CC_customer_ID",
        "tracking_code",
        "dispatched",
        "canceled",
        "redemption_file",
        "proof_of_delivery_file",
    )
    list_display = (
        "__str__",
        "deal",
        "wowcher_code",
        "customer_name",
        "CC_order_ID",
        "tracking_code",
        "dispatched",
        "canceled",
        "on_redemption_file",
        "on_proof_of_delivery_file",
        "time_created",
    )
    list_display_links = ("__str__",)
    list_editable = ("dispatched", "canceled")
    search_fields = (
        "deal__deal_ID",
        "deal__name",
        "wowcher_code",
        "CC_order_ID",
        "CC_customer_ID",
        "tracking_code",
    )
    list_filter = ("dispatched", "canceled")


class WowcherFileAdmin(admin.ModelAdmin):
    """Model admin for wowcher files."""

    list_display = ("__str__", "time_created")


@admin.register(models.WowcherRedemptionFile)
class WowcherRedemptionFileAdmin(WowcherFileAdmin):
    """Model Admin for the WowcherRedemptionFile model."""


@admin.register(models.WowcherProofOfDeliveryFile)
class WowcherProofOfDeliveryFileAdmin(WowcherFileAdmin):
    """Model Admin for the WowcherProofOfDeliveryFile model."""


@admin.register(models.WowcherStockLevelCheck)
class WowcherStockLevelCheckAdmin(admin.ModelAdmin):
    """Model admin for the WowcherStockLevelCheck model."""

    list_display = ("get_deal", "get_SKU", "item", "stock_level", "timestamp")
    list_editable = ("stock_level",)
