"""Model admin for price_calculator app."""

from django.contrib import admin

from price_calculator import models


@admin.register(models.DestinationCountry)
class DestinationCountryAdmin(admin.ModelAdmin):
    """Model admin for DestinationCountry model."""

    fields = ("name", "currency_code", "min_channel_fee")
    list_display = ("name", "currency_code", "min_channel_fee")
    list_editable = ("currency_code", "min_channel_fee")
    search_fields = ("name",)


@admin.register(models.PackageType)
class PackageTypeAdmin(admin.ModelAdmin):
    """Model admin for PackageType model."""

    fields = ("name",)
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(models.ShippingPrice)
class ShippingPriceAdmin(admin.ModelAdmin):
    """Model admin for ShippingPrice model."""

    fields = (
        "name",
        "country",
        "package_type",
        "min_weight",
        "max_weight",
        "min_price",
        "max_price",
        "item_price",
        "kilo_price",
        "vat_rates",
        "disabled",
    )
    list_display = (
        "__str__",
        "name",
        "package_type_string",
        "country",
        "min_weight",
        "max_weight",
        "min_price",
        "max_price",
        "item_price",
        "kilo_price",
        "disabled",
    )
    list_display_links = ("__str__",)
    list_editable = (
        "name",
        "country",
        "min_weight",
        "max_weight",
        "min_price",
        "max_price",
        "item_price",
        "kilo_price",
        "disabled",
    )
    list_filter = ("package_type", "country", "vat_rates", "disabled")
    search_fields = ("name",)


@admin.register(models.VATRate)
class VATRateAdmin(admin.ModelAdmin):
    """Model admin for VATRate model."""

    fields = ("name", "cc_id", "percentage")
    list_display = ("__str__", "name", "cc_id", "percentage")
    list_display_links = ("__str__",)
    list_editable = ("name", "cc_id", "percentage")
    search_fields = ("name",)
