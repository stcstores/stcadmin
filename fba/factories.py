"""Model factories for the fba app."""

import datetime as dt

import factory
from factory.django import DjangoModelFactory

from fba import models
from home.factories import StaffFactory
from inventory.factories import ProductFactory
from shipping.factories import CountryFactory, CurrencyFactory


class FBARegionFactory(DjangoModelFactory):
    class Meta:
        model = models.FBARegion

    name = factory.Faker("text", max_nb_chars=200)
    country = factory.SubFactory(CountryFactory)
    postage_price = factory.Faker("pyint", max_value=5000, min_value=0)
    postage_per_kg = factory.Faker("pyint", max_value=500, min_value=0)
    postage_overhead_g = factory.Faker("pyint", max_value=500, min_value=0)
    max_weight = factory.Faker("pyint", max_value=2000, min_value=0)
    max_size = factory.Faker("pyfloat", positive=True, right_digits=2)
    fulfillment_unit = models.FBARegion.METRIC
    currency = factory.SubFactory(CurrencyFactory)
    warehouse_required = True
    expiry_date_required = False
    position = 9999
    auto_close = False
    active = True


class FBAOrderFactory(DjangoModelFactory):
    class Meta:
        model = models.FBAOrder

    class Params:
        not_processed = False
        awaiting_booking = False
        printed = False
        on_hold = False
        fulfilled = False

        fulfilled_by_required = factory.LazyAttribute(
            lambda o: True if o.fulfilled else False
        )
        closed_at_required = factory.LazyAttribute(
            lambda o: True if o.fulfilled else False
        )
        quantity_sent_required = factory.LazyAttribute(
            lambda o: True if o.fulfilled or o.awaiting_booking else False
        )
        box_weight_required = factory.LazyAttribute(
            lambda o: True if (o.fulfilled or o.awaiting_booking) else False
        )
        is_printed = factory.LazyAttribute(
            lambda o: True if o.fulfilled or o.awaiting_booking or o.printed else False
        )

    fulfilled_by = factory.Maybe(
        "fulfilled_by_required",
        factory.SubFactory(StaffFactory),
        None,
    )
    closed_at = factory.Maybe(
        "closed_at_required",
        factory.Faker("date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc),
        None,
    )
    region = factory.SubFactory(FBARegionFactory)
    product = factory.SubFactory(ProductFactory)
    product_weight = factory.Faker("pyint", min_value=0, max_value=5000)
    product_asin = factory.Faker("pystr", min_chars=14, max_chars=14)
    product_purchase_price = "52.49"
    product_is_multipack = False
    selling_price = factory.Faker("pyint", min_value=10, max_value=5000)
    FBA_fee = factory.Faker("pyint", min_value=10, max_value=5000)
    aproximate_quantity = factory.Faker("pyint", min_value=1, max_value=500)
    quantity_sent = factory.Maybe(
        "quantity_sent_required",
        factory.Faker("pyint", min_value=1, max_value=500),
        None,
    )
    box_weight = factory.Maybe(
        "box_weight_required",
        factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True),
        None,
    )
    notes = factory.Faker("sentence")
    priority = models.FBAOrder.MAX_PRIORITY
    printed = factory.Maybe("is_printed", True, False)
    small_and_light = factory.Faker("pybool")
    on_hold = factory.LazyAttribute(lambda o: o.on_hold)
    update_stock_level_when_complete = True
    is_combinable = False
    is_fragile = False
