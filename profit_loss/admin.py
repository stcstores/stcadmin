"""Model admin for profit loss models."""

from django.contrib import admin
from profit_loss import models


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    """Model admin for Order model."""

    fields = (
        "order_id",
        "department",
        "shipping_service",
        "country",
        "weight",
        "vat_rate",
        "price",
        "purchase_price",
        "postage_price",
        "item_count",
        "date_recieved",
        "dispatch_date",
    )
    list_display = (
        "__str__",
        "order_id",
        "department",
        "shipping_service",
        "country",
        "weight",
        "vat_rate",
        "price",
        "purchase_price",
        "postage_price",
        "item_count",
        "date_recieved",
        "dispatch_date",
        "profit",
    )
    list_display_links = ("__str__",)
    search_fields = ("order_id",)
    list_filter = ("dispatch_date", "department", "shipping_service", "country")

    def __repr__(self):
        return str(self.order_id)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    """Model admin for Product model."""

    fields = ("sku", "name", "range_id", "product_id", "quantity", "order")
    list_display = ("id", "sku", "name", "range_id", "product_id", "quantity", "order")
