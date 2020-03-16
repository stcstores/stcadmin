"""Model admin for the orders app."""
from django.contrib import admin

from orders import models


@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Admin for the Channel model."""

    fields = ("name",)
    list_display = ("__str__", "name")
    list_editable = ("name",)


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
    )
    list_display = (
        "__str__",
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
    )
    list_editable = ("cancelled", "ignored", "shipping_rule", "courier_service")


@admin.register(models.ProductSale)
class ProductSaleAdmin(admin.ModelAdmin):
    """Admin for the ProductSale model."""

    fields = ("order", "product_ID", "quantity", "price")
    list_display = ("order", "product_ID", "quantity", "price")


@admin.register(models.PackingRecord)
class PackingRecordAdmin(admin.ModelAdmin):
    """Admin for the PackingRecord model."""

    fields = ("order", "packed_by")
    list_display = ("order", "packed_by")
    list_editable = ("packed_by",)


@admin.register(models.OrderUpdate)
class OrderUpdateAdmin(admin.ModelAdmin):
    """Admin for the OrderUpdate models."""

    fields = ("status", "started_at", "completed_at")
    list_display = ("__str__", "status", "started_at", "completed_at")
    list_editable = ("status",)
    list_filter = ("status",)
