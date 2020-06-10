import factory
import pytest_factoryboy
from django.utils import timezone

from home.models import CloudCommerceUser
from orders import models
from shipping.tests.conftest import (
    CountryFactory,
    CourierServiceFactory,
    ShippingRuleFactory,
)

pytest_factoryboy.register(CountryFactory)
pytest_factoryboy.register(ShippingRuleFactory)
pytest_factoryboy.register(CourierServiceFactory)


@pytest_factoryboy.register
class CloudCommerceUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = CloudCommerceUser

    user_id = factory.Sequence(lambda n: str(5641616 + n))
    stcadmin_user = None
    first_name = factory.Faker("first_name")
    second_name = factory.Faker("last_name")
    hidden = False


@pytest_factoryboy.register
class ChannelFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Channel

    name = factory.Sequence(lambda n: f"Test Channel {n}")


@pytest_factoryboy.register
class OrderFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Order

    order_ID = factory.Sequence(lambda n: str(748373 + n))
    customer_ID = factory.Sequence(lambda n: str(16844161 + n))
    recieved_at = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    dispatched_at = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    cancelled = False
    ignored = False
    channel = factory.SubFactory(ChannelFactory)
    channel_order_ID = factory.Sequence(lambda n: str(6413545 + n))
    country = factory.SubFactory(CountryFactory)
    shipping_rule = factory.SubFactory(ShippingRuleFactory)
    courier_service = factory.SubFactory(CourierServiceFactory)
    tracking_number = factory.Sequence(lambda n: f"TK8493833{n}")


@pytest_factoryboy.register
class PackingRecordFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PackingRecord

    order = factory.SubFactory(OrderFactory)
    packed_by = factory.SubFactory(CloudCommerceUserFactory)


@pytest_factoryboy.register
class ProductSaleFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ProductSale

    order = factory.SubFactory(OrderFactory)
    product_ID = factory.Sequence(lambda n: str(6546486 + n))
    quantity = 1
    price = 550


@pytest_factoryboy.register
class BreakageFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Breakage

    product_sku = factory.Sequence(lambda n: f"ABC-123-56{n}")
    order_id = factory.Sequence(lambda n: str(4684684 + n))
    note = ""
    packer = factory.SubFactory(CloudCommerceUserFactory)
    timestamp = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())


@pytest_factoryboy.register
class OrderUpdateFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrderUpdate

    started_at = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    completed_at = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    status = models.OrderUpdate.COMPLETE
