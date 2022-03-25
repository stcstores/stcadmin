import factory
import pytest_factoryboy

from inventory.models import PackageType
from inventory.tests.conftest import ProductRangeFactory
from price_calculator import models
from shipping.tests.conftest import (
    CountryFactory,
    ShippingPriceFactory,
    ShippingServiceFactory,
)

pytest_factoryboy.register(CountryFactory)
pytest_factoryboy.register(ShippingServiceFactory)
pytest_factoryboy.register(ShippingPriceFactory)
pytest_factoryboy.register(ProductRangeFactory)


@pytest_factoryboy.register
class CountryChannelFeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CountryChannelFee

    country = factory.SubFactory(CountryFactory)
    min_channel_fee = 7


@pytest_factoryboy.register
class ProductTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProductType

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
class ChannelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Channel

    name = factory.Sequence(lambda n: f"Test Channel {n}")
    ordering = 100


@pytest_factoryboy.register
class ShippingMethodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ShippingMethod

    name = factory.Sequence(lambda n: f"Test Shipping Price {n}")
    country = factory.SubFactory(CountryFactory)
    shipping_service = factory.SubFactory(ShippingServiceFactory)


@pytest_factoryboy.register
class PackageTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PackageType

    name = factory.sequence(lambda n: f"Test Package Type {n}")
    active = True
