"""Model Admin for the shipping app."""
from django.contrib import admin


class CurrencyAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Currency."""

    fields = ("name", "code", "exchange_rate")
    list_display = ("name", "code", "exchange_rate")
    list_editable = ("code", "exchange_rate")


class CountryAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Country."""

    fields = ("country_ID", "name", "region", "currency")
    list_display = ("__str__", "country_ID", "name", "region", "currency")
    list_editable = ("country_ID", "name", "region", "currency")
    list_filter = ("region", "country")


class ProviderAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Provider."""

    fields = ("name",)
    list_display = ("__str__", "name")
    list_editable = ("name",)


class ServiceAdmin(admin.ModelAdmin):
    """Model Admin for shipping.Service."""

    fields = ("name", "provider")
    list_display = ("__str__", "name", "provider")
    list_editable = ("name", "provider")


class ShippingRuleAdmin(admin.ModelAdmin):
    """Model Admmin for shipping.ShippingRule."""

    fields = ("rule_ID", "name", "service", "inactive")
    list_display = ("__str__", "rule_ID", "name", "service", "inactive")
    list_editable = ("rule_ID", "name", "service", "inactive")
    list_filter = ("service", "service__provider")
