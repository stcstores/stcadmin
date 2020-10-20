"""Model Admin for the FBA app."""

from django.contrib import admin

from fba import models


@admin.register(models.FBARegion)
class FBARegionAdmin(admin.ModelAdmin):
    """Model admin for the FBARegion model."""

    fields = [
        "name",
        "postage_price",
        "max_weight",
        "max_size",
        "dimension_unit",
        "weight_unit",
        "currency",
        "auto_close",
    ]
    list_display = [
        "name",
        "postage_price",
        "max_weight",
        "max_size",
        "dimension_unit",
        "weight_unit",
        "currency",
        "auto_close",
    ]
    list_editable = [
        "postage_price",
        "max_weight",
        "max_size",
        "dimension_unit",
        "weight_unit",
        "currency",
        "auto_close",
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
        "fullfilled_by",
        "closed_at",
        "region",
        "product_SKU",
        "product_ID",
        "product_name",
        "selling_price",
        "FBA_fee",
        "aproximate_quantity",
        "quantity_sent",
        "box_width",
        "box_height",
        "box_depth",
        "box_weight",
        "notes",
        "priority",
    ]

    list_display = [
        "__str__",
        "status",
        "created_at",
        "modified_at",
        "fullfilled_by",
        "closed_at",
        "region",
        "product_SKU",
        "product_ID",
        "product_name",
        "selling_price",
        "FBA_fee",
        "aproximate_quantity",
        "quantity_sent",
        "box_width",
        "box_height",
        "box_depth",
        "box_weight",
        "notes",
        "priority",
    ]

    search_fields = ["product_SKU", "product_ID", "product_name"]

    date_hierarchy = "created_at"

    list_filter = ["region", "status"]
