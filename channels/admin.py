"""Admin for the channels app."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from channels import models


@admin.register(models.DefaultContact)
class DefaultContactAdmin(SingletonModelAdmin):
    """Admin for the Default Contact model."""

    fields = ("phone", "email")


@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Admin for the Channel model."""

    fields = ("name", "channel_id")
    list_display = ("__str__", "name", "channel_id")
    list_editable = ("name", "channel_id")


@admin.register(models.CreatedOrder)
class CreatedOrderAdmin(admin.ModelAdmin):
    """Admin for the CreatedOrder model."""

    fields = (
        "customer_id",
        "order_id",
        "billing_address_id",
        "delivery_address_id",
        "invoice_id",
    )
    list_display = fields
    search_fields = ("customer_id", "order_id")


@admin.register(models.WishImport)
class WishImportAdmin(admin.ModelAdmin):
    """Admin for the WishImport model."""

    fields = ("created_at",)
    list_display = ("created_at",)


@admin.register(models.WishOrder)
class WishOrderAdmin(admin.ModelAdmin):
    """Admin for the WishOrder model."""

    fields = (
        "wish_import",
        "wish_transaction_id",
        "wish_order_id",
        "order",
        "fulfiled",
        "error",
    )
    list_display = (
        "wish_import",
        "wish_transaction_id",
        "wish_order_id",
        "order",
        "fulfiled",
        "is_on_fulfilment_export",
        "error",
    )


@admin.register(models.WishBulkFulfilmentExport)
class WishBulkFulfilmentExportAdmin(admin.ModelAdmin):
    """Admin for the WishBulkFulfilmentExport model."""

    fields = ("created_at", "completed_at", "download_file", "error_message")
    list_display = (
        "__str__",
        "created_at",
        "completed_at",
        "download_file",
        "error_message",
    )


@admin.register(models.ShopifyConfig)
class ShopifyConfigAdmin(SingletonModelAdmin):
    """Admin for the ShopifyConfig model."""

    fields = ("channel_id",)


@admin.register(models.ShopifyImport)
class ShopifyImportAdmin(admin.ModelAdmin):
    """Admin for the ShopifyImport model."""

    fields = ("created_at",)
    list_display = ("created_at",)


@admin.register(models.ShopifyOrder)
class ShopifyOrderAdmin(admin.ModelAdmin):
    """Admin for the ShopifyOrder model."""

    fields = (
        "shopify_import",
        "shopify_order_id",
        "order",
        "fulfiled",
        "error",
    )
    list_display = (
        "shopify_import",
        "shopify_order_id",
        "order",
        "fulfiled",
        "error",
    )


@admin.register(models.ShopifyFulfillmentError)
class ShopifyFulfillmentErrorAdmin(admin.ModelAdmin):
    """Admin for the ShopifyFulfillmentError model."""

    fields = ("shopify_order", "error")
    list_display = ("shopify_order", "error")
