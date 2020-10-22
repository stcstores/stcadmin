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
        "dimension_unit",
        "weight_unit",
        "currency",
        "auto_close",
        "flag",
    ]
    list_display = [
        "name",
        "default_country",
        "postage_price",
        "max_weight",
        "max_size",
        "dimension_unit",
        "weight_unit",
        "currency",
        "auto_close",
        "flag",
    ]
    list_editable = [
        "default_country",
        "postage_price",
        "max_weight",
        "max_size",
        "dimension_unit",
        "weight_unit",
        "currency",
        "auto_close",
        "flag",
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
        "FBA_fee",
        "selling_price",
        "small_and_light",
        "aproximate_quantity",
        "quantity_sent",
        "box_width",
        "box_height",
        "box_depth",
        "box_weight",
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
        "small_and_light",
        "selling_price",
        "FBA_fee",
        "aproximate_quantity",
        "quantity_sent",
        "box_width",
        "box_height",
        "box_depth",
        "box_weight",
        "priority",
        "fulfilled_by",
    ]

    search_fields = ["product_SKU", "product_ID", "product_name"]

    date_hierarchy = "created_at"

    list_filter = ["region", "status"]
