from datetime import datetime

import factory
import pytest_factoryboy
from django.utils import timezone

from home.factories import StaffFactory
from inventory.models import Supplier
from orders import models
from shipping.factories import (
    CountryFactory,
    CurrencyFactory,
    ProviderFactory,
    ShippingPriceFactory,
    ShippingServiceFactory,
    WeightBandFactory,
)

pytest_factoryboy.register(CountryFactory)
pytest_factoryboy.register(ShippingServiceFactory)
pytest_factoryboy.register(ShippingPriceFactory)
pytest_factoryboy.register(WeightBandFactory)
pytest_factoryboy.register(ProviderFactory)
pytest_factoryboy.register(StaffFactory)


@pytest_factoryboy.register
class SupplierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Supplier

    name = factory.Sequence(lambda n: f"Test Supplier {n}")
    active = True


@pytest_factoryboy.register
class ChannelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Channel

    name = factory.Sequence(lambda n: f"Test Channel {n}")
    channel_fee = 15.5
    include_vat = True


@pytest_factoryboy.register
class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Order

    order_id = factory.Sequence(lambda n: str(748373 + n))
    recieved_at = timezone.make_aware(datetime(2020, 2, 11, 10, 24))
    dispatched_at = timezone.make_aware(datetime(2020, 2, 10, 12, 36))
    cancelled = False
    ignored = False
    channel = factory.SubFactory(ChannelFactory)
    external_reference = factory.Sequence(lambda n: str(6413545 + n))
    country = factory.SubFactory(CountryFactory)
    shipping_service = factory.SubFactory(ShippingServiceFactory)
    tracking_number = factory.Sequence(lambda n: f"TK8493833{n}")
    priority = False
    priority = False
    displayed_shipping_price = 832
    calculated_shipping_price = 846
    tax = 2560
    currency = factory.SubFactory(CurrencyFactory)
    exchange_rate = factory.Faker("pydecimal", left_digits=1, right_digits=3)
    tax_GBP = 1530
    total_paid = 4457
    total_paid_GBP = 5691
    packed_by = factory.SubFactory(StaffFactory)


@pytest_factoryboy.register
class ProductSaleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProductSale

    order = factory.SubFactory(OrderFactory)
    sku = factory.Sequence(lambda n: f"ABC-123-TG{n}")
    channel_sku = factory.Sequence(lambda n: f"AMZ_{n}")
    name = factory.Sequence(lambda n: f"Test Product {n}")
    weight = 256
    quantity = 1
    supplier = factory.SubFactory(SupplierFactory)
    purchase_price = 250
    tax = 12
    unit_price = 518
    item_price = 518
    item_total_before_tax = 489
