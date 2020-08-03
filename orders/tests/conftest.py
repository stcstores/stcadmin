from datetime import datetime

import factory
import pytest_factoryboy
from django.utils import timezone

from home.models import CloudCommerceUser
from inventory.models import Department, Supplier
from orders import models
from shipping.tests.conftest import (
    CountryFactory,
    CourierServiceFactory,
    ProviderFactory,
    ShippingPriceFactory,
    ShippingRuleFactory,
    VatRateFactory,
)

pytest_factoryboy.register(CountryFactory)
pytest_factoryboy.register(ShippingRuleFactory)
pytest_factoryboy.register(ShippingPriceFactory)
pytest_factoryboy.register(CourierServiceFactory)
pytest_factoryboy.register(VatRateFactory)
pytest_factoryboy.register(ProviderFactory)


@pytest_factoryboy.register
class DepartmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"Test Department {n}")
    product_option_value_ID = factory.Sequence(lambda n: str(6465 + n))
    abriviation = "TD"
    inactive = False


@pytest_factoryboy.register
class SupplierFactory(factory.DjangoModelFactory):
    class Meta:
        model = Supplier

    name = factory.Sequence(lambda n: f"Test Supplier {n}")
    product_option_value_ID = factory.Sequence(lambda n: str(6465 + n))
    factory_ID = factory.Sequence(lambda n: str(n + 46546))
    inactive = False


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
    recieved_at = timezone.make_aware(datetime(2020, 2, 11, 10, 24))
    dispatched_at = timezone.make_aware(datetime(2020, 2, 10, 12, 36))
    cancelled = False
    ignored = False
    channel = factory.SubFactory(ChannelFactory)
    channel_order_ID = factory.Sequence(lambda n: str(6413545 + n))
    country = factory.SubFactory(CountryFactory)
    shipping_rule = factory.SubFactory(ShippingRuleFactory)
    courier_service = factory.SubFactory(CourierServiceFactory)
    tracking_number = factory.Sequence(lambda n: f"TK8493833{n}")
    total_paid = 4457
    total_paid_GBP = 5691
    priority = False
    postage_price = 832
    postage_price_success = True


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
    sku = factory.Sequence(lambda n: f"ABC-123-TG{n}")
    name = factory.Sequence(lambda n: f"Test Product {n}")
    weight = 256
    quantity = 1
    price = 550
    department = factory.SubFactory(DepartmentFactory)
    purchase_price = 250
    vat_rate = 20
    supplier = factory.SubFactory(SupplierFactory)
    details_success = True


@pytest_factoryboy.register
class OrderUpdateFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrderUpdate

    started_at = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    completed_at = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    status = models.OrderUpdate.COMPLETE


@pytest_factoryboy.register
class OrderDetailsUpdateFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrderDetailsUpdate

    started_at = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    completed_at = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    status = models.OrderDetailsUpdate.COMPLETE


@pytest_factoryboy.register
class OrderDetailsUpdateErrorFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.OrderDetailsUpdateError

    update = factory.SubFactory(OrderDetailsUpdateFactory)
    product_sale = factory.SubFactory(ProductSaleFactory)
    text = "An exception string"


@pytest_factoryboy.register
class RefundFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Refund

    order = factory.SubFactory(OrderFactory)
    notes = "A refund"
    closed = False


@pytest_factoryboy.register
class BreakageRefundFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.BreakageRefund

    order = factory.SubFactory(OrderFactory)
    contact_contacted = False
    refund_accepted = None
    refund_amount = 982
    notes = "A refund for a damaged item"
    closed = False
    supplier = factory.SubFactory(SupplierFactory)


@pytest_factoryboy.register
class PackingMistakeRefundFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.PackingMistakeRefund

    order = factory.SubFactory(OrderFactory)
    notes = "A refund for a packing mistake"
    closed = False


@pytest_factoryboy.register
class LinkingMistakeRefundFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.LinkingMistakeRefund

    order = factory.SubFactory(OrderFactory)
    notes = "A refund for a linking mistake"
    closed = False


@pytest_factoryboy.register
class LostInPostRefundFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.LostInPostRefund

    order = factory.SubFactory(OrderFactory)
    contact_contacted = False
    refund_accepted = None
    refund_amount = 982
    notes = "A refund for an item lost in the post"
    closed = False
    courier = factory.SubFactory(ProviderFactory)


@pytest_factoryboy.register
class DemicRefundFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.DemicRefund

    order = factory.SubFactory(OrderFactory)
    contact_contacted = False
    refund_accepted = None
    refund_amount = 982
    notes = "A refund for an item recieved from the supplier damaged"
    closed = False
    supplier = factory.SubFactory(SupplierFactory)


@pytest_factoryboy.register
class ProductRefundFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ProductRefund

    refund = factory.SubFactory(LostInPostRefundFactory)
    product = factory.SubFactory(ProductSaleFactory)
    quantity = 1


@pytest_factoryboy.register
class RefundImageFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.RefundImage

    refund = factory.SubFactory(RefundFactory)
    product_refund = None
    image = factory.django.ImageField(width=1000, height=1000)
    thumbnail = factory.django.ImageField(width=200, height=200)
