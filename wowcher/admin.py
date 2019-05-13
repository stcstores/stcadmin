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
        "ended",
        "inactive",
    )
    list_display_links = ("__str__",)
    list_editable = ("deal_ID", "name", "shipping_price", "ended", "inactive")
    list_filter = ("inactive",)
    search_fields = ("deal_ID", "name")


@admin.register(models.WowcherItem)
class WowcherItemAdmin(admin.ModelAdmin):
    """ModelAdmin for the WowcherItem model."""

    fields = ("deal", "wowcher_ID", "CC_SKU", "CC_product_ID")
    list_display = ("__str__", "deal", "wowcher_ID", "CC_SKU", "CC_product_ID")
    list_display_links = ("__str__",)
    list_editable = ("deal", "wowcher_ID", "CC_SKU", "CC_product_ID")
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

    @admin.register(models.WowcherRedemptionFile)
    class WowcherRedemptionFileAdmin(admin.ModelAdmin):
        """Model Admin for the WowcherRedemptionFile model."""

        list_display = ("__str__", "time_created")

    @admin.register(models.WowcherProofOfDeliveryFile)
    class WowcherProofOfDeliveryFileAdmin(admin.ModelAdmin):
        """Model Admin for the WowcherProofOfDeliveryFile model."""

        list_display = ("__str__", "time_created")
