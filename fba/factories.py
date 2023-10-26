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

    fulfilled_by = None
    closed_at = None
    region = factory.SubFactory(FBARegionFactory)
    product = factory.SubFactory(ProductFactory)
    product_weight = factory.Faker("pyint", min_value=0, max_value=5000)
    product_hs_code = factory.Faker("pystr", min_chars=14, max_chars=14)
    product_asin = factory.Faker("pystr", min_chars=14, max_chars=14)
    product_purchase_price = "52.49"
    product_is_multipack = False
    selling_price = factory.Faker("pyint", min_value=10, max_value=5000)
    FBA_fee = factory.Faker("pyint", min_value=10, max_value=5000)
    aproximate_quantity = factory.Faker("pyint", min_value=1, max_value=500)
    quantity_sent = None
    box_weight = None
    notes = factory.Faker("sentence")
    priority = models.FBAOrder.MAX_PRIORITY
    printed = False
    small_and_light = False
    on_hold = False
    update_stock_level_when_complete = True
    is_combinable = False
    is_fragile = False
    is_stopped = False
    stopped_at = None
    stopped_until = None
    stopped_reason = None

    class Params:
        status_not_processed = factory.Trait(
            fulfilled_by=None,
            closed_at=None,
            quantity_sent=None,
            box_weight=None,
            printed=False,
            on_hold=False,
            is_stopped=False,
            stopped_reason=None,
            stopped_at=None,
            stopped_until=None,
        )
        status_ready = factory.Trait(
            fulfilled_by=None,
            closed_at=None,
            quantity_sent=factory.Faker("pyint", min_value=1, max_value=500),
            box_weight=factory.Faker(
                "pydecimal", left_digits=2, right_digits=2, positive=True
            ),
            printed=True,
            on_hold=False,
            is_stopped=False,
            stopped_reason=None,
            stopped_at=None,
            stopped_until=None,
        )
        status_printed = factory.Trait(
            fulfilled_by=None,
            closed_at=None,
            quantity_sent=None,
            box_weight=None,
            printed=True,
            on_hold=False,
            is_stopped=False,
            stopped_reason=None,
            stopped_at=None,
            stopped_until=None,
        )
        status_on_hold = factory.Trait(
            fulfilled_by=None,
            closed_at=None,
            quantity_sent=None,
            box_weight=None,
            printed=False,
            on_hold=True,
            is_stopped=False,
            stopped_reason=None,
            stopped_at=None,
            stopped_until=None,
        )
        status_fulfilled = factory.Trait(
            fulfilled_by=factory.SubFactory(StaffFactory),
            closed_at=factory.Faker(
                "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
            ),
            quantity_sent=factory.Faker("pyint", min_value=1, max_value=500),
            box_weight=factory.Faker(
                "pydecimal", left_digits=2, right_digits=2, positive=True
            ),
            printed=True,
            on_hold=False,
            is_stopped=False,
            stopped_reason=None,
            stopped_at=None,
            stopped_until=None,
        )
        status_stopped = factory.Trait(
            fulfilled_by=None,
            closed_at=None,
            quantity_sent=None,
            box_weight=None,
            printed=True,
            on_hold=False,
            is_stopped=True,
            stopped_reason=factory.Faker("sentence"),
            stopped_at=factory.Faker(
                "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
            ),
            stopped_until=factory.Faker(
                "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
            ),
        )
