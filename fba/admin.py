"""Model Admin for the FBA app."""

from django.contrib import admin

from fba import models


@admin.register(models.FBACountry)
class FBACountryAdmin(admin.ModelAdmin):
    """Model admin for the FBA Country model."""

    fields = [
        "country",
        "postage_price",
        "max_weight",
        "max_size",
        "extra_countries",
        "dimension_unit",
        "weight_unit",
    ]
    list_display = [
        "country",
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
