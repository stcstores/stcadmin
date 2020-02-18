"""Shipping Models."""
import json
from pathlib import Path

import requests
from ccapi import CCAPI
from django.conf import settings
from django.db import models
from django.utils import timezone


class Currency(models.Model):
    """Model for currencies."""

    EXCHANGE_RATE_URL = "https://api.exchangerate-api.com/v4/latest/GBP"

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=5, unique=True)
    exchange_rate = models.DecimalField(max_digits=6, decimal_places=3)
    symbol = models.CharField(max_length=5, default="$")

    class Meta:
        """Meta class for Currency."""

        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.name

    @classmethod
    def update(cls):
        """Update the exchange rates."""
        response = requests.get(cls.EXCHANGE_RATE_URL)
        response.raise_for_status()
        rates = response.json()["rates"]
        for currency in cls._default_manager.all():
            currency.exchange_rate = 1 / rates[currency.code]
            currency.save()


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


class ShippingRule(models.Model):
    """Model for Shipping Rules."""

    rule_ID = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=255, unique=True)
    courier_service = models.ForeignKey(
        CourierService, blank=True, null=True, on_delete=models.PROTECT
    )
    priority = models.BooleanField(default=False)
    inactive = models.BooleanField(default=False)

    class Meta:
        """Meta class for shipping.ShippingRule."""

        verbose_name = "Shipping Rule"
        verbose_name_plural = "Shipping Rules"
        ordering = ("inactive", "name")

    def __str__(self):
        return self.name

    @classmethod
    def update(cls):
        """Update shipping rules from Cloud Commerce."""
        rules = CCAPI.get_courier_rules()
        cls._backup_rules(rules)
        cls._remove_defunct_rules(rules)
        for rule in rules:
            cls._create_or_update_from_cc_rule(rule)

    @classmethod
    def _backup_path(cls):
        filename = f"shipping_rules_{timezone.now().strftime('%Y-%m-%d')}.json"
        return Path(settings.MEDIA_ROOT) / "shipping_rules" / filename

    @classmethod
    def _backup_rules(cls, rules):
        path = cls._backup_path()
        directory = path.parent
        directory.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            json.dump(rules.json, f, indent=4, sort_keys=True)

    @classmethod
    def _remove_defunct_rules(cls, rules):
        rule_ids = [rule.id for rule in rules]
        cls.objects.exclude(rule_ID__in=rule_ids).update(inactive=True)

    @classmethod
    def _get_rule_kwargs(cls, cc_rule):
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

    @classmethod
    def _create_or_update_from_cc_rule(cls, cc_rule):
        kwargs = cls._get_rule_kwargs(cc_rule)
        queryset = cls.objects.filter(rule_ID=cc_rule.id)
        if queryset.exists():
            queryset.update(**kwargs)
        else:
            cls.objects.create(**kwargs)
