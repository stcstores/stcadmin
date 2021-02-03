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
