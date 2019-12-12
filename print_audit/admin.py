"""Model admin for print_audit."""

from django.contrib import admin

from print_audit import models


@admin.register(models.CloudCommerceOrder)
class CloudCommerceOrderAdmin(admin.ModelAdmin):
    """Model admin for CloudCommerceOrder model."""

    list_display = (
        "order_id",
        "user",
        "date_created",
        "date_completed",
        "attempts",
        "customer_id",
    )
    date_hierarchy = "date_created"
    list_filter = ("user", "date_created")
    list_editable = ("user",)


@admin.register(models.Breakage)
class BreakageAdmin(admin.ModelAdmin):
    """Model admin for Breackage model."""

    fields = ("product_sku", "order_id", "packer")
    list_display = ("__str__", "product_sku", "order_id", "note", "packer", "timestamp")
    list_display_links = ("__str__",)
    list_editable = ("product_sku", "order_id", "packer")
    date_hierarchy = "timestamp"
    search_fields = ("order_id", "product_sku")
    list_filter = ("packer",)
