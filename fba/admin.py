"""Model Admin for the FBA app."""

from django.contrib import admin

from fba import models


@admin.register(models.FBARegion)
class FBARegionAdmin(admin.ModelAdmin):
    """Model admin for the FBARegion model."""

    fields = [
        "name",
        "default_country",
        "postage_price",
        "max_weight",
        "max_size",
        "fulfillment_unit",
        "currency",
        "auto_close",
        "warehouse_required",
    ]
    list_display = [
        "name",
        "default_country",
        "postage_price",
        "max_weight",
        "max_size",
        "fulfillment_unit",
        "currency",
        "auto_close",
        "warehouse_required",
    ]
    list_editable = [
        "default_country",
        "postage_price",
        "max_weight",
        "max_size",
        "fulfillment_unit",
        "currency",
        "auto_close",
        "warehouse_required",
    ]


@admin.register(models.FBACountry)
class FBACountryAdmin(admin.ModelAdmin):
    """Model admin for the FBACountry model."""

    fields = ["region", "country"]
    list_display = ["__str__", "region", "country"]
    list_editable = ["region", "country"]


@admin.register(models.FBAOrder)
class FBAOrderAdmin(admin.ModelAdmin):
    """Model admin for the FBAOrder models."""

    fields = [
        "region",
        "product_SKU",
        "product_ID",
        "product_name",
        "product_weight",
        "product_hs_code",
        "product_asin",
        "product_image_url",
        "product_purchase_price",
        "FBA_fee",
        "selling_price",
        "small_and_light",
        "on_hold",
        "is_combinable",
        "aproximate_quantity",
        "quantity_sent",
        "box_weight",
        "tracking_number",
        "closed_at",
        "fulfilled_by",
        "notes",
        "priority",
    ]

    list_display = [
        "__str__",
        "status",
        "region",
        "created_at",
        "modified_at",
        "notes",
        "closed_at",
        "product_SKU",
        "product_ID",
        "product_name",
        "product_weight",
        "product_hs_code",
        "product_asin",
        "product_purchase_price",
        "small_and_light",
        "on_hold",
        "is_combinable",
        "selling_price",
        "FBA_fee",
        "aproximate_quantity",
        "quantity_sent",
        "box_weight",
        "tracking_number",
        "priority",
        "fulfilled_by",
    ]

    search_fields = [
        "product_SKU",
        "product_ID",
        "product_name",
        "product_asin",
        "tracking_number",
    ]

    date_hierarchy = "created_at"

    list_filter = ["region", "status"]


@admin.register(models.FBAShippingPrice)
class FBAShippingPriceAdmin(admin.ModelAdmin):
    """Model admin for the FBAShippingPrice model."""

    fields = ["product_SKU", "price_per_item"]
    list_display = ["__str__", "product_SKU", "price_per_item", "added"]
    list_editable = ["product_SKU", "price_per_item"]
