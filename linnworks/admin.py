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
    list_display = ("sub_source", "source", "link_prime", "channel")
    list_editable = ("channel",)
    search_fields = ("sub_source", "source")
    list_select_related = ("channel",)
    autocomplete_fields = ("channel",)


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


@admin.register(models.StockLevelExportUpdate)
class StockLevelExportUpdateAdmin(admin.ModelAdmin):
    """Model admin for the StockLevelExportUpdate model."""

    exclude_fields = ()
    list_display = ("export_time", "stock_count", "stock_value")
    date_hierarchy = "export_time"
    search_fields = ("export_time",)


@admin.register(models.StockLevelExportRecord)
class StockLevelExportRecordAdmin(admin.ModelAdmin):
    """Model admin for the StockLevelExportRecord model."""

    exclude_fields = ()
    list_display = (
        "stock_level_update",
        "product",
        "stock_level",
        "purchase_price",
        "stock_value",
        "in_order_book",
    )
    date_hierarchy = "stock_level_update__export_time"
    search_fields = (
        "product__sku",
        "product__name",
    )
    list_select_related = ("stock_level_update", "product")
    autocomplete_fields = ("stock_level_update", "product")


@admin.register(models.LinnworksOrder)
class LinnworksOrderAdmin(admin.ModelAdmin):
    """Model admin for the LinnworksOrder model."""

    exclude_fields = ()
    readonly_fields = ("order",)
    list_display = ("order", "order_guid")
    search_fields = ("order__order_id", "order_guid")
    list_select_related = ("order",)
    date_hierarchy = "order__dispatched_at"
