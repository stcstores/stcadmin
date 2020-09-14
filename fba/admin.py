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
    ]
    list_display = [
        "name",
        "postage_price",
        "max_weight",
        "max_size",
        "dimension_unit",
        "weight_unit",
    ]
    list_editable = [
        "postage_price",
        "max_weight",
        "max_size",
        "dimension_unit",
        "weight_unit",
    ]


@admin.register(models.FBACountry)
class FBACountryAdmin(admin.ModelAdmin):
    """Model adming for the FBACountry model."""

    fields = ["region", "country"]
    list_display = ["__str__", "region", "country"]
    list_editable = ["region", "country"]
