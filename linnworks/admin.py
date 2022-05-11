"""Model Admin for the Linnworks app."""

from django.contrib import admin
from solo.admin import SingletonModelAdmin

from linnworks import models


@admin.register(models.LinnworksConfig)
class LinnworksConfigAdmin(SingletonModelAdmin):
    """Model admin for the LinnworksConfig model."""

    exclude_fields = ()


@admin.register(models.LinnworksChannel)
class LinnworksChannelAdmin(admin.ModelAdmin):
    """Model admin for the LinnworksChannel model."""

    exclude_fields = ()


@admin.register(models.LinkingIgnoredSKU)
class LinkingIgnoredSKUAdmin(admin.ModelAdmin):
    """Model admin for the LinkingIgnoredSKU model."""

    exclude_fields = ()


@admin.register(models.InitialStockLevel)
class InitialStockLevelAdmin(admin.ModelAdmin):
    """Model admin for the InitialStoclLevel model."""

    exclude_fields = ()
    list_display = ("sku", "stock_level")
    list_editable = ("stock_level",)
    search_fields = ("sku",)
