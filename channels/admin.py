"""Admin for the channels app."""

from django.contrib import admin

from channels import models


@admin.register(models.ShopifyImport)
class ShopifyImportAdmin(admin.ModelAdmin):
    """Admin for the ShopifyImport model."""

    fields = ("created_at",)
    list_display = ("created_at",)
