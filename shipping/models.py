"""Shipping Models."""

import datetime as dt
import math

import requests
from django.db import models


class CurrencyManager(models.Manager):
    """Model Manager for the Currency model."""

    def update_rates(self):
        """Update the exchange rates."""
        response = requests.get(Currency.EXCHANGE_RATE_URL)
        response.raise_for_status()
        rates = response.json()["rates"]
        date = dt.date.today()
        for currency in self.all():
            rate = 1 / rates[currency.code]
            ExchangeRate(currency=currency, date=date, rate=rate).save()


class Currency(models.Model):
    """Model for currencies."""

    EXCHANGE_RATE_URL = "https://api.exchangerate-api.com/v4/latest/GBP"

    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=5, unique=True)
    symbol = models.CharField(max_length=5, default="$")

    objects = CurrencyManager()

    class Meta:
        """Meta class for Currency."""

        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.name

    def exchange_rate(self, date=None):
        """Return the exchange rate for this currency.

        Args:
            date (datetime.date, optional): The date to return the exchange rate for.
                If None it will return the latest exchange rate. Defaults to None.

        Returns:
            Decimal: The exchange rate between this currency and GBP.
        """
        if date is None:
            exchange_rate = self.exchange_rates.latest()
        else:
            exchange_rate = self.exchange_rates.get(date=date)
        return exchange_rate.rate


class ExchangeRate(models.Model):
    """Model for currency exchange rates."""

    currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, related_name="exchange_rates"
    )
    date = models.DateField()
    rate = models.DecimalField(max_digits=6, decimal_places=3)

    class Meta:
        """Meta class for ExchageRate."""

        verbose_name = "Exchange Rate"
        verbose_name_plural = "Exchange Rates"
        ordering = ("-date",)
        get_latest_by = "date"
        unique_together = ("currency", "date")


class Region(models.Model):
    """Model for shipping regions."""

    VAT_ALWAYS = "Always"
    VAT_NEVER = "Never"
    VAT_VARIABLE = "Variable"

    VAT_REQUIRED_CHOICES = (
        (VAT_ALWAYS, VAT_ALWAYS),
        (VAT_NEVER, VAT_NEVER),
        (VAT_VARIABLE, VAT_VARIABLE),
    )

    name = models.CharField(max_length=255)
    abriviation = models.CharField(max_length=10, blank=True, null=True)
    vat_required = models.CharField(
        max_length=10, choices=VAT_REQUIRED_CHOICES, default=VAT_VARIABLE
    )
    default_vat_rate = models.FloatField(default=20)
    flag_if_not_delivered_by_days = models.PositiveSmallIntegerField(null=True)

    class Meta:
        """Meta class for the Region model."""

        verbose_name = "Region"
        verbose_name_plural = "Regions"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Country(models.Model):
    """Model for shipping countries."""

    VAT_ALWAYS = Region.VAT_ALWAYS
    VAT_NEVER = Region.VAT_NEVER
    VAT_VARIABLE = Region.VAT_VARIABLE
    VAT_FROM_REGION = "As Region"

    VAT_REQUIRED_CHOICES = (
        (VAT_ALWAYS, VAT_ALWAYS),
        (VAT_NEVER, VAT_NEVER),
        (VAT_VARIABLE, VAT_VARIABLE),
        (VAT_FROM_REGION, VAT_FROM_REGION),
    )

    name = models.CharField(max_length=255)
    ISO_code = models.CharField(max_length=2, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    currency = models.ForeignKey(
        Currency, blank=True, null=True, on_delete=models.SET_NULL
    )
    vat_required = models.CharField(
        max_length=10,
        choices=VAT_REQUIRED_CHOICES,
        default=VAT_FROM_REGION,
    )
    default_vat_rate = models.FloatField(blank=True, null=True)
    flag = models.ImageField(upload_to="flags", blank=True, null=True)

    class Meta:
        """Meta class for Country."""

        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ("name",)

    def __str__(self):
        return self.name

    def vat_is_required(self):
        """Return True if VAT is required for this country, otherwise False."""
        if self.vat_required == self.VAT_FROM_REGION:
            return self.region.vat_required
        return self.vat_required

    def vat_rate(self):
        """Return the default VAT rate for the country or region."""
        if self.default_vat_rate is not None:
            return self.default_vat_rate
        return self.region.default_vat_rate


class Provider(models.Model):
    """Model for shipping providers."""

    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=False)

    class Meta:
        """Meta class for shipping.Provider."""

        verbose_name = "Provider"
        verbose_name_plural = "Providers"
        ordering = ("-active", "name")

    def __str__(self):
        return self.name


class ShippingService(models.Model):
    """Model for shipping services."""

    name = models.CharField(max_length=255, unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    provider = models.ForeignKey(
        Provider,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        limit_choices_to={"active": True},
    )
    priority = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        """Meta class for shipping.ShippingService."""

        verbose_name = "Shipping Service"
        verbose_name_plural = "Shipping Services"
        ordering = ("-active", "name")

    def __str__(self):
        return self.name


class ShippingPriceManager(models.Manager):
    """Model manager for the ShippingPrice model."""

    def find_shipping_price(self, country, shipping_service):
        """Return the shipping price object for a given country and shipping service."""
        try:
            return self.get(country=country, shipping_service=shipping_service)
        except ShippingPrice.DoesNotExist:
            return self.get(region=country.region, shipping_service=shipping_service)


class ShippingPrice(models.Model):
    """Model for shipping prices."""

    shipping_service = models.ForeignKey(
        ShippingService, on_delete=models.CASCADE, limit_choices_to={"active": True}
    )
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=True, null=True
    )
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)
    item_price = models.PositiveIntegerField(default=0)
    price_per_kg = models.PositiveIntegerField(default=0)
    price_per_g = models.DecimalField(max_digits=7, decimal_places=3, default=0)
    item_surcharge = models.PositiveIntegerField(default=0)
    fuel_surcharge = models.PositiveIntegerField(default=0)
    covid_surcharge = models.PositiveIntegerField(default=0)

    active = models.BooleanField(default=False)

    objects = ShippingPriceManager()

    class Meta:
        """Meta class for shipping.ShippingPrice."""

        verbose_name = "Shipping Price"
        verbose_name_plural = "Shipping Prices"
        ordering = ("-active", "shipping_service__name")

        unique_together = [
            ["shipping_service", "country"],
            ["shipping_service", "region"],
        ]
        constraints = [
            models.CheckConstraint(
                name="shipping_price_has_country_or_region",
                condition=(
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
        price = 0
        price += self.item_price
        price += self._per_kg_price(weight)
        price += self._per_g_price(weight)
        if self.weightband_set.count() > 0:
            price += self._weight_band_price(weight)
        price += price * (self.fuel_surcharge / 100)
        price += self.item_surcharge
        price += self.covid_surcharge
        return round(price)

    def _per_kg_price(self, weight):
        weight_kg = math.ceil(weight / 1000)
        return self.price_per_kg * weight_kg

    def _per_g_price(self, weight):
        return math.ceil(self.price_per_g * weight)

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
