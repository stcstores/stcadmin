import factory
import pytest_factoryboy

from price_calculator import models
from shipping.tests.conftest import CountryFactory

pytest_factoryboy.register(CountryFactory)


@pytest_factoryboy.register
class DestinationCountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DestinationCountry

    name = factory.Sequence(lambda n: f"Test Destination Country {n}")
    country = factory.SubFactory(CountryFactory)
    min_channel_fee = 7


@pytest_factoryboy.register
class PackageTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PackageType

    name = factory.Sequence(lambda n: f"Test Package Type {n}")


@pytest_factoryboy.register
class VatRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.VATRate

    name = factory.Sequence(lambda n: f"Test VAT Rate {n}")
    cc_id = factory.Sequence(lambda n: n + 3)
    percentage = 37


@pytest_factoryboy.register
class ChannelFeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ChannelFee

    name = factory.Sequence(lambda n: f"Test Channel Fee {n}")
    fee_percentage = 13
    ordering = 100


@pytest_factoryboy.register
class ShippingPriceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ShippingPrice

    name = factory.Sequence(lambda n: f"Test Shipping Price {n}")
    country = factory.SubFactory(DestinationCountryFactory)
    item_price = 540
    kilo_price = 230
