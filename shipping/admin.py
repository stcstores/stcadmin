"""Model Admin for the shipping app."""

from django.contrib import admin

from shipping import models
from stcadmin.admin import actions


@admin.register(models.Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Currency."""

    fields = ("name", "code", "exchange_rate", "symbol")
    list_display = ("name", "code", "exchange_rate", "symbol")
    list_editable = ("code", "symbol")
    search_fields = ("name", "symbol", "code")


@admin.register(models.ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    """Model admin for the ExchagneRate model."""

    exclude = ()
    list_display = ("date", "currency", "rate")
    list_filter = ("currency",)
    search_fields = ("currency__name", "currency__code")
    autocomplete_fields = ("currency",)
    list_select_related = ("currency",)
    date_hierarchy = "date"


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
        "name",
        "region",
        "ISO_code",
        "currency",
        "vat_required",
        "flag",
        "default_vat_rate",
    )
    list_filter = ("region", "currency", "vat_required")
    search_fields = ("name", "ISO_code")
    autocomplete_fields = ("region", "currency")
    list_select_related = ("region", "currency")


@admin.register(models.Provider)
class ProviderAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Provider."""

    exclude = ()
    list_display = ("__str__", "name", "active")
    list_editable = ("name", "active")
    search_fields = ("name",)
    list_filter = ("active",)
    actions = (actions.set_active, actions.set_inactive)


@admin.action(description="Set Priority")
def set_priority(modeladmin, request, queryset):
    """Set inactive action."""
    queryset.update(priority=True)


@admin.action(description="Unset priority")
def unset_priority(modeladmin, request, queryset):
    """Set active action."""
    queryset.update(priority=False)


@admin.register(models.ShippingService)
class ShippingServiceAdmin(admin.ModelAdmin):
    """Model admin for shipping.ShippingService."""

    exclude = ()
    list_display = ("name", "provider", "full_name", "priority", "active")
    list_editable = ("active",)
    search_fields = ("name", "full_name", "provider__name")
    list_filter = ("active", "provider")
    list_select_related = ("provider",)
    autocomplete_fields = ("provider",)
    actions = (actions.set_active, actions.set_inactive, set_priority, unset_priority)


@admin.register(models.ShippingPrice)
class ShippingPriceAdmin(admin.ModelAdmin):
    """Model admin for shipping.ShippingPrice."""

    exclude = ()
    list_display = (
        "__str__",
        "shipping_service",
        "country",
        "region",
        "item_price",
        "price_per_kg",
        "price_per_g",
        "item_surcharge",
        "fuel_surcharge",
        "covid_surcharge",
        "active",
    )
    list_editable = (
        "item_price",
        "price_per_kg",
        "price_per_g",
        "item_surcharge",
        "fuel_surcharge",
        "covid_surcharge",
        "active",
    )
    list_filter = (
        "active",
        ("shipping_service", admin.RelatedOnlyFieldListFilter),
        ("country", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "shipping_service__name",
        "shipping_service__full_name",
        "country__name",
    )
    list_select_related = ("shipping_service", "country", "region")
    autocomplete_fields = ("shipping_service", "country", "region")


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
    search_fields = (
        "shipping_price__name",
        "country__name",
        "shipping_price__shipping_service__name",
        "shipping_price__shipping_service__full_name",
    )
    list_select_related = ("shipping_price",)
