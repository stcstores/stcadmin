"""Model admin for price_calculator app."""

from django.contrib import admin

from price_calculator import models


@admin.register(models.DestinationCountry)
class DestinationCountryAdmin(admin.ModelAdmin):
    """Model admin for DestinationCountry model."""

    fields = ("name", "country", "min_channel_fee", "sort_order")
    list_display = ("name", "country", "min_channel_fee", "sort_order")
    list_editable = ("country", "min_channel_fee", "sort_order")
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


@admin.register(models.ChannelFee)
class ChannelFeeAdmin(admin.ModelAdmin):
    """Model admin for the ChannelFee model."""

    fields = ("name", "fee_percentage", "ordering")
    list_display = ("__str__", "name", "fee_percentage", "ordering")
    list_display_links = ("__str__",)
    list_editable = ("name", "fee_percentage", "ordering")
