"""Model admin for the orders app."""
from django.contrib import admin

from orders import models


@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Admin for the Channel model."""

    fields = ("name", "channel_fee", "include_vat")
    list_display = ("__str__", "name", "channel_fee", "include_vat")
    list_editable = ("name", "channel_fee", "include_vat")


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for the Order model."""

    fields = (
        "order_ID",
        "customer_ID",
        "recieved_at",
        "dispatched_at",
        "cancelled",
        "ignored",
        "channel",
        "channel_order_ID",
        "country",
        "shipping_rule",
        "courier_service",
        "tracking_number",
        "total_paid",
        "total_paid_GBP",
        "postage_price",
        "postage_price_success",
    )
    list_display = (
        "__str__",
        "order_ID",
        "recieved_at",
        "dispatched_at",
        "cancelled",
        "ignored",
        "country",
        "shipping_rule",
        "courier_service",
        "total_paid",
        "total_paid_GBP",
        "postage_price",
        "postage_price_success",
    )
    search_fields = ("order_ID", "customer_ID")
    list_editable = ("cancelled", "ignored")


@admin.register(models.ProductSale)
class ProductSaleAdmin(admin.ModelAdmin):
    """Admin for the ProductSale model."""

    fields = (
        "order",
        "product_ID",
        "sku",
        "name",
        "quantity",
        "price",
        "weight",
        "purchase_price",
        "vat_rate",
        "supplier",
        "details_success",
    )
    readonly_fields = ("order",)
    list_display = (
        "order",
        "product_ID",
        "sku",
        "name",
        "quantity",
        "price",
        "weight",
        "purchase_price",
        "vat_rate",
        "supplier",
        "details_success",
    )
    search_fields = (
        "order__order_ID",
        "order__customer_ID",
        "sku",
        "name",
        "product_ID",
    )


@admin.register(models.PackingRecord)
class PackingRecordAdmin(admin.ModelAdmin):
    """Admin for the PackingRecord model."""

    fields = (
        "__str__",
        "order",
        "packed_by",
    )
    readonly_fields = ("order",)
    list_display = ("order", "packed_by")
    list_editable = ("packed_by",)


@admin.register(models.OrderUpdate)
class OrderUpdateAdmin(admin.ModelAdmin):
    """Admin for the OrderUpdate models."""

    fields = ("started_at", "status", "completed_at")
    readonly_fields = ("started_at",)
    list_display = ("__str__", "status", "started_at", "completed_at")
    list_editable = ("status",)
    list_filter = ("status",)


@admin.register(models.OrderDetailsUpdate)
class OrderDetailsUpdateAdmin(admin.ModelAdmin):
    """Admin for the OrderDetailsUpdate model."""

    fields = ("started_at", "completed_at", "status")
    readonly_fields = ("started_at",)
    list_display = ("started_at", "completed_at", "status")
    list_editable = ("status",)


@admin.register(models.OrderDetailsUpdateError)
class OrderDetailsUpdateErrorAdmin(admin.ModelAdmin):
    """Admin for the OrderDetailsUpdateError model."""

    fields = ("update", "product_sale", "text")
    list_display = ("update", "product_sale", "text")
