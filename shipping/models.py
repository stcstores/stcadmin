"""Shipping Models."""
from django.db import models


class Currency(models.Model):
    """Model for currencies."""

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=5, unique=True)
    exchange_rate = models.DecimalField(max_digits=6, decimal_places=3)

    class Meta:
        """Meta class for Currency."""

        verbose_name = "Currency"
        verbose_name_plural = "Currencies"


class Country(models.Model):
    """Model for shipping countries."""

    EU = "EU"
    EUROPE = "Europe"
    UK = "UK"
    ROW = "ROW"
    REST_OF_WORLD = "Rest of World"
    REGION_CHOICES = ((EU, EUROPE), (UK, UK), (ROW, REST_OF_WORLD))

    country_ID = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    ISO_code = models.CharField(max_length=2, blank=True, null=True)
    region = models.CharField(max_length=3, choices=REGION_CHOICES)
    currency = models.ForeignKey(
        Currency, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        """Meta class for Country."""

        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ("country_ID",)


class Provider(models.Model):
    """Model for shipping providers."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        """Meta class for shipping.Provider."""

        verbose_name = "Provider"
        verbose_name_plural = "Providers"


class Service(models.Model):
    """Model for shipping services."""

    name = models.CharField(max_length=255)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)

    class Meta:
        """Meta class for shipping.Service."""

        verbose_name = "Service"
        verbose_name_plural = "Services"
        unique_together = ("name", "provider")


class ShippingRule(models.Model):
    """Model for Shipping Rules."""

    rule_ID = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255, unique=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    priority = models.BooleanField(default=False)
    inactive = models.BooleanField(default=False)

    class Meta:
        """Meta class for shipping.ShippingRule."""

        verbose_name = "Shipping Rule"
        verbose_name_plural = "Shipping Rules"
