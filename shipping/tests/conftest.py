from decimal import Decimal

import factory
import pytest_factoryboy

from shipping import models


@pytest_factoryboy.register
class CurrencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Currency

    name = factory.Sequence(lambda n: f"Test Currency {n}")
    code = factory.Sequence(lambda n: f"SD{n}")
    exchange_rate = Decimal(1.45)
    symbol = "$"


@pytest_factoryboy.register
class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Region

    name = factory.Sequence(lambda n: f"Test Currency {n}")
    abriviation = "EU"
    vat_required = True


@pytest_factoryboy.register
class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Country

    country_ID = factory.Sequence(lambda n: f"15{n}")
    name = factory.Sequence(lambda n: f"Test Country {n}")
    ISO_code = "TC"
    region = factory.SubFactory(RegionFactory)
    currency = factory.SubFactory(CurrencyFactory)
    vat_required = None


@pytest_factoryboy.register
class ProviderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Provider

    name = factory.Sequence(lambda n: f"Test Provider {n}")
    inactive = False


@pytest_factoryboy.register
class CourierTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CourierType

    courier_type_ID = factory.Sequence(lambda n: f"116{n}")
    name = factory.Sequence(lambda n: f"Test Courier Type {n}")
    provider = factory.SubFactory(ProviderFactory)
    inactive = False


@pytest_factoryboy.register
class CourierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Courier

    courier_ID = factory.Sequence(lambda n: f"116{n}")
    name = factory.Sequence(lambda n: f"Test Courier {n}")
    courier_type = factory.SubFactory(CourierTypeFactory)
    inactive = False


@pytest_factoryboy.register
class CourierServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CourierService

    courier_service_ID = factory.Sequence(lambda n: f"23{n}")
    name = factory.Sequence(lambda n: f"Test Courier Service {n}")
    courier = factory.SubFactory(CourierFactory)
    inactive = False


@pytest_factoryboy.register
class ShippingRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ShippingRule

    rule_ID = factory.Sequence(lambda n: f"1000{n}")
    name = factory.Sequence(lambda n: f"Test Shipping Rule {n}")
    courier_service = factory.SubFactory(CourierServiceFactory)
    priority = False
    inactive = False


@pytest_factoryboy.register
class ShippingServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ShippingService

    name = factory.Sequence(lambda n: f"Test Shipping Service {n}")


@pytest_factoryboy.register
class ShippingPriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ShippingPrice

    shipping_service = factory.SubFactory(ShippingServiceFactory)
    country = factory.SubFactory(CountryFactory)
    region = None
    item_price = 550
    price_per_kg = 0
    inactive = False


@pytest_factoryboy.register
class WeightBandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.WeightBand

    shipping_price = factory.SubFactory(ShippingPriceFactory)
    min_weight = 200
    max_weight = 500
    price = 720
