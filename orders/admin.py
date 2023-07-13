"""Model admin for the orders app."""
from django.contrib import admin

from orders import models
from stcadmin.admin import actions


@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Admin for the Channel model."""

    exclude = ()
    list_display = ("name", "channel_fee", "include_vat", "active")
    list_editable = ("channel_fee", "include_vat", "active")
    search_fields = ("name",)
    actions = (actions.set_active, actions.set_inactive)


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for the Order model."""

    exclude = ()
    list_display = (
        "order_id",
        "external_reference",
        "recieved_at",
        "dispatched_at",
        "cancelled",
        "ignored",
        "country",
        "shipping_service",
        "packed_by",
    )
    search_fields = ("order_id", "external_reference")
    list_editable = ("cancelled", "ignored")
    list_filter = (
        ("shipping_service", admin.RelatedOnlyFieldListFilter),
        ("country", admin.RelatedOnlyFieldListFilter),
    )
    date_hierarchy = "recieved_at"
    list_select_related = ("country", "shipping_service")
    autocomplete_fields = ("country", "shipping_service")


@admin.register(models.ProductSale)
class ProductSaleAdmin(admin.ModelAdmin):
    """Admin for the ProductSale model."""

    exclude = ()
    list_display = (
        "order",
        "sku",
        "channel_sku",
        "name",
        "weight",
        "quantity",
        "supplier",
        "purchase_price",
        "tax",
        "unit_price",
        "item_price",
        "item_total_before_tax",
    )
    search_fields = (
        "order__order_id",
        "sku",
        "name",
    )
    list_select_related = ("order", "supplier")
    autocomplete_fields = ("order", "supplier")


@admin.register(models.OrderExportDownload)
class OrderExportDownloadAdmin(admin.ModelAdmin):
    """Model admin for the OrderExportDownload model."""

    exclude = ()
    list_display = (
        "status",
        "created_at",
        "completed_at",
        "error_message",
        "download_file",
    )
    date_hierarchy = "created_at"


@admin.register(models.PackingMistake)
class PackingMistakeAdmin(admin.ModelAdmin):
    """Model admin for the PackingMistake model."""

    exclude = ()
    list_display = ("user", "timestamp", "order_id", "note")
    date_hierarchy = "timestamp"
    list_filter = (("user", admin.RelatedOnlyFieldListFilter),)
