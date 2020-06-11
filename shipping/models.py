"""Shipping Models."""
import json
import math
from pathlib import Path

import requests
from ccapi import CCAPI
from django.conf import settings
from django.db import models
from django.utils import timezone


class CurrencyManager(models.Manager):
    """Model Manager for the Currency model."""

    def update_rates(self):
        """Update the exchange rates."""
        response = requests.get(Currency.EXCHANGE_RATE_URL)
        response.raise_for_status()
        rates = response.json()["rates"]
        for currency in self.all():
            currency.exchange_rate = 1 / rates[currency.code]
            currency.save()


class Currency(models.Model):
    """Model for currencies."""

    EXCHANGE_RATE_URL = "https://api.exchangerate-api.com/v4/latest/GBP"

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=5, unique=True)
    exchange_rate = models.DecimalField(max_digits=6, decimal_places=3)
    symbol = models.CharField(max_length=5, default="$")

    objects = CurrencyManager()

    class Meta:
        """Meta class for Currency."""

        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.name


class Region(models.Model):
    """Model for shipping regions."""

    name = models.CharField(max_length=255)
    abriviation = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        """Meta class for the Region model."""

        verbose_name = "Region"
        verbose_name_plural = "Regions"
        ordering = ("name",)

    def __str__(self):
        return self.name


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
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    currency = models.ForeignKey(
        Currency, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        """Meta class for Country."""

        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ("country_ID",)

    def __str__(self):
        return self.name


class Provider(models.Model):
    """Model for shipping providers."""

    name = models.CharField(max_length=255, unique=True)
    inactive = models.BooleanField(default=False)

    class Meta:
        """Meta class for shipping.Provider."""

        verbose_name = "Provider"
        verbose_name_plural = "Providers"

    def __str__(self):
        return self.name


class CourierType(models.Model):
    """Model for Cloud Commerce courier types."""

    courier_type_ID = models.CharField(max_length=12, unique=True, db_index=True)
    name = models.CharField(max_length=255, unique=True)
    provider = models.ForeignKey(
        Provider, null=True, blank=True, on_delete=models.PROTECT
    )
    inactive = models.BooleanField(default=False)

    class Meta:
        """Meta class for shipping.CourierType."""

        verbose_name = "Courier Type"
        verbose_name_plural = "Courier Types"

    def __str__(self):
        return self.name


class Courier(models.Model):
    """Model for Cloud Commerce courier types."""

    courier_ID = models.CharField(max_length=12, unique=True, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    courier_type = models.ForeignKey(
        CourierType, on_delete=models.PROTECT, null=True, blank=True
    )
    inactive = models.BooleanField(default=False)

    class Meta:
        """Meta class for shipping.CourierType."""

        verbose_name = "Courier"
        verbose_name_plural = "Couriers"

    def __str__(self):
        return f"{self.courier_ID}: {self.name}"


class CourierService(models.Model):
    """Model for Cloud Commerce courier types."""

    courier_service_ID = models.CharField(max_length=12, unique=True, db_index=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    courier = models.ForeignKey(
        Courier, on_delete=models.PROTECT, null=True, blank=True
    )
    inactive = models.BooleanField(default=False)

    class Meta:
        """Meta class for shipping.CourierType."""

        verbose_name = "Courier Service"
        verbose_name_plural = "Couriers Services"

    def __str__(self):
        return f"{self.courier_service_ID}: {self.name}"


class ShippingService(models.Model):
    """Model for shipping services."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        """Meta class for shipping.ShippingService."""

        verbose_name = "Shipping Service"
        verbose_name_plural = "Shipping Services"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ShippingPrice(models.Model):
    """Model for shipping prices."""

    FIXED = "fixed"
    WEIGHT = "weight"
    WEIGHT_BAND = "weight_band"
    PRICE_TYPES = ((FIXED, "Fixed"), (WEIGHT, "Weight"), (WEIGHT_BAND, "Weight Band"))

    shipping_service = models.ForeignKey(ShippingService, on_delete=models.CASCADE)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True
    )
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
    price_type = models.CharField(max_length=50, choices=PRICE_TYPES)
    item_price = models.IntegerField(default=0)
    price_per_kg = models.IntegerField(default=0)
    inactive = models.BooleanField(default=False)

    class Meta:
        """Meta class for shipping.ShippingPrice."""

        verbose_name = "Shipping Price"
        verbose_name_plural = "Shipping Prices"

        unique_together = [
            ["shipping_service", "country"],
            ["shipping_service", "region"],
        ]
        constraints = [
            models.CheckConstraint(
                name="shipping_price_has_country_or_region",
                check=(
                    models.Q(country__isnull=False, region__isnull=True)
                    | models.Q(country__isnull=True, region__isnull=False)
                ),
            )
        ]

    def __str__(self):
        if self.country is not None:
            location = self.country
        else:
            location = self.region
        return f"{self.shipping_service} - {location}"

    def price(self, weight):
        """Return the shipping price for a given weight in grams."""
        if self.price_type == self.FIXED:
            return self._fixed_price()
        elif self.price_type == self.WEIGHT:
            return self._weight_price(weight)
        elif self.price_type == self.WEIGHT_BAND:
            return self._weight_band_price(weight)
        else:
            raise NotImplementedError(
                f"No price method exists for price type {self.price_type}"
            )

    def _fixed_price(self):
        return self.item_price

    def _weight_price(self, weight):
        weight_kg = math.ceil(weight / 1000)
        return self.item_price + self.price_per_kg * weight_kg

    def _weight_band_price(self, weight):
        return self.weightband_set.get(
            min_weight__lte=weight, max_weight__gte=weight
        ).price


class WeightBand(models.Model):
    """Model for shipping price weight bands."""

    shipping_price = models.ForeignKey(ShippingPrice, on_delete=models.CASCADE)
    min_weight = models.IntegerField()
    max_weight = models.IntegerField()
    price = models.IntegerField()

    class Meta:
        """Meta clss for shiping.WeightBand."""

        verbose_name = "Weight Band"
        verbose_name_plural = "Weight Bands"
        ordering = ("min_weight",)

    def __str__(self):
        return f"{self.shipping_price} {self.min_weight}g - {self.max_weight}g"


class ShippingRuleManager(models.Manager):
    """Model Manager for the ShippingRule model."""

    def update_rules(self):
        """Update shipping rules from Cloud Commerce."""
        rules = CCAPI.get_courier_rules()
        self._backup_rules(rules)
        self._remove_defunct_rules(rules)
        for rule in rules:
            self._create_or_update_from_cc_rule(rule)

    def _backup_path(self):
        filename = f"shipping_rules_{timezone.now().strftime('%Y-%m-%d')}.json"
        return Path(settings.MEDIA_ROOT) / "shipping_rules" / filename

    def _backup_rules(self, rules):
        path = self._backup_path()
        directory = path.parent
        directory.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            json.dump(rules.json, f, indent=4, sort_keys=True)

    def _remove_defunct_rules(self, rules):
        rule_ids = [rule.id for rule in rules]
        self.exclude(rule_ID__in=rule_ids).update(inactive=True)

    def _get_rule_kwargs(self, cc_rule):
        courier, _ = Courier.objects.get_or_create(
            courier_ID=str(cc_rule.courier_services_group_id)
        )
        courier_service, _ = CourierService.objects.get_or_create(
            courier_service_ID=str(cc_rule.courier_services_rule_id),
            defaults={"courier": courier},
        )
        return {
            "rule_ID": cc_rule.id,
            "name": cc_rule.name,
            "courier_service": courier_service,
            "priority": bool(cc_rule.is_priority),
            "inactive": False,
        }

    def _create_or_update_from_cc_rule(self, cc_rule):
        kwargs = self._get_rule_kwargs(cc_rule)
        queryset = self.filter(rule_ID=cc_rule.id)
        if queryset.exists():
            queryset.update(**kwargs)
        else:
            self.create(**kwargs)


class ShippingRule(models.Model):
    """Model for Shipping Rules."""

    rule_ID = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=255, unique=True)
    courier_service = models.ForeignKey(
        CourierService, blank=True, null=True, on_delete=models.PROTECT
    )
    shipping_service = models.ForeignKey(
        ShippingService, blank=True, null=True, on_delete=models.PROTECT
    )
    priority = models.BooleanField(default=False)
    inactive = models.BooleanField(default=False)

    objects = ShippingRuleManager()

    class Meta:
        """Meta class for shipping.ShippingRule."""

        verbose_name = "Shipping Rule"
        verbose_name_plural = "Shipping Rules"
        ordering = ("inactive", "name")

    def __str__(self):
        return self.name
