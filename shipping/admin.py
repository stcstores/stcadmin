"""Model Admin for the shipping app."""

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from shipping import models


@admin.register(models.Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Currency."""

    fields = ("name", "code", "exchange_rate", "symbol")
    list_display = ("name", "code", "exchange_rate", "symbol")
    list_editable = ("code", "exchange_rate", "symbol")
    search_fields = ("name", "symbol", "code")


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    """Model admin for shipping.Region."""

    fields = (
        "name",
        "abriviation",
        "vat_required",
        "default_vat_rate",
        "flag_if_not_delivered_by_days",
    )
    list_display = (
        "id",
        "name",
        "abriviation",
        "vat_required",
        "default_vat_rate",
        "flag_if_not_delivered_by_days",
    )
    list_editable = (
        "name",
        "abriviation",
        "vat_required",
        "default_vat_rate",
        "flag_if_not_delivered_by_days",
    )
    search_fields = ("name",)


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Country."""

    exclude = ()
    list_display = (
        "__str__",
        "country_ID",
        "name",
        "region",
        "currency",
        "vat_required",
        "flag",
        "default_vat_rate",
    )
    list_editable = (
        "country_ID",
        "name",
        "region",
        "currency",
        "vat_required",
        "default_vat_rate",
    )
    list_filter = ("region", "currency", "vat_required")
    search_fields = ("name",)
    search_fields = ("name",)
    autocomplete_fields = ("region", "currency")
    list_select_related = ("region", "currency")


@admin.register(models.Provider)
class ProviderAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Provider."""

    fields = ("name",)
    list_display = ("__str__", "name")
    list_editable = ("name",)


@admin.register(models.CourierType)
class CourierTypeAdmin(admin.ModelAdmin):
    """Model Admin for shipping.CourierType."""

    fields = ("courier_type_ID", "name", "provider", "inactive")
    list_display = ("__str__", "courier_type_ID", "name", "provider", "inactive")
    list_editable = ("name", "courier_type_ID", "provider", "inactive")


@admin.register(models.Courier)
class CourierAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Courier."""

    fields = ("courier_ID", "name", "courier_type", "inactive")
    list_display = ("__str__", "courier_ID", "name", "courier_type", "inactive")
    list_editable = ("courier_ID", "name", "courier_type", "inactive")
    list_filter = ("courier_type",)


@admin.register(models.CourierService)
class CourierServiceAdmin(admin.ModelAdmin):
    """Model Admin for shipping.CourierService."""

    fields = ("courier_service_ID", "name", "courier", "inactive")
    list_display = ("__str__", "courier_service_ID", "name", "courier", "inactive")
    list_editable = ("courier_service_ID", "name", "courier", "inactive")
    list_filter = ("courier",)


@admin.register(models.ShippingService)
class ShippingServiceAdmin(admin.ModelAdmin):
    """Model admin for shipping.ShippingService."""

    fields = ("name",)
    list_display = ("id", "name")
    list_editable = ("name",)


@admin.register(models.ShippingPrice)
class ShippingPriceAdmin(admin.ModelAdmin):
    """Model admin for shipping.ShippingPrice."""

    fields = (
        "shipping_service",
        "country",
        "region",
        "item_price",
        "price_per_kg",
        "price_per_g",
        "item_surcharge",
        "fuel_surcharge",
        "covid_surcharge",
        "inactive",
    )
    list_display = (
        "id",
        "shipping_service",
        "country",
        "region",
        "item_price",
        "price_per_kg",
        "price_per_g",
        "item_surcharge",
        "fuel_surcharge",
        "covid_surcharge",
        "inactive",
    )
    list_editable = (
        "item_price",
        "price_per_kg",
        "price_per_g",
        "item_surcharge",
        "fuel_surcharge",
        "covid_surcharge",
        "inactive",
    )
    list_filter = (
        ("shipping_service", admin.RelatedOnlyFieldListFilter),
        ("country", admin.RelatedOnlyFieldListFilter),
    )


@admin.register(models.WeightBand)
class WeightBandAdmin(admin.ModelAdmin):
    """Model admin for shipping.WeightBand."""

    fields = ("shipping_price", "min_weight", "max_weight", "price")
    list_display = fields
    list_editable = ("min_weight", "max_weight", "price")
    list_filter = (
        ("shipping_price__shipping_service", admin.RelatedOnlyFieldListFilter),
        ("shipping_price__country", admin.RelatedOnlyFieldListFilter),
    )


@admin.register(models.ShippingRule)
class ShippingRuleAdmin(admin.ModelAdmin):
    """Model Admmin for shipping.ShippingRule."""

    fields = ("rule_ID", "name", "courier_service", "shipping_service", "inactive")
    list_display = (
        "__str__",
        "rule_ID",
        "name",
        "courier_service",
        "shipping_service",
        "inactive",
    )
    list_editable = (
        "rule_ID",
        "name",
        "courier_service",
        "shipping_service",
        "inactive",
    )


@admin.register(models.VATRate)
class VATRateAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for the VATRate model."""

    fields = ("name", "cc_id", "percentage")
    list_display = ("__str__", "name", "cc_id", "percentage")
    list_display_links = ("__str__",)
    list_editable = ("name", "cc_id", "percentage")
    search_fields = ("name",)
