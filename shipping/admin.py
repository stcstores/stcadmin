"""Model Admin for the shipping app."""
from django.contrib import admin

from shipping import models


@admin.register(models.Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Currency."""

    fields = ("name", "code", "exchange_rate", "symbol")
    list_display = ("name", "code", "exchange_rate", "symbol")
    list_editable = ("code", "exchange_rate", "symbol")


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Country."""

    fields = ("country_ID", "name", "region", "currency")
    list_display = ("__str__", "country_ID", "name", "region", "currency")
    list_editable = ("country_ID", "name", "region", "currency")
    list_filter = ("region",)


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


@admin.register(models.ShippingRule)
class ShippingRuleAdmin(admin.ModelAdmin):
    """Model Admmin for shipping.ShippingRule."""

    fields = ("rule_ID", "name", "courier_service", "inactive")
    list_display = ("__str__", "rule_ID", "name", "courier_service", "inactive")
    list_editable = ("rule_ID", "name", "courier_service", "inactive")
