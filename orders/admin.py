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
    list_filter = (("packed_by", admin.RelatedOnlyFieldListFilter),)
    list_select_related = ("packed_by",)
    autocomplete_fields = ("packed_by",)
