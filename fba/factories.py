"""Model factories for the fba app."""

import datetime as dt

import factory
from factory.django import DjangoModelFactory

from fba import models
from home.factories import StaffFactory, UserFactory
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
    min_shipping_cost = factory.Faker("pyint", max_value=500, min_value=0)
    placement_fee = 30
    max_weight = factory.Faker("pyint", max_value=2000, min_value=0)
    max_size = factory.Faker("pyfloat", positive=True, right_digits=2)
    fulfillment_unit = models.FBARegion.METRIC
    currency = factory.SubFactory(CurrencyFactory)
    warehouse_required = False
    expiry_date_required = False
    position = 9999
    auto_close = False
    active = True


class FBAOrderFactory(DjangoModelFactory):
    class Meta:
        model = models.FBAOrder

    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    modified_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
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
    priority = False
    printed = False
    small_and_light = False
    on_hold = False
    update_stock_level_when_complete = True
    is_combinable = False
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


class FBATrackingNumberFactory(DjangoModelFactory):
    class Meta:
        model = models.FBATrackingNumber

    fba_order = factory.SubFactory(FBAOrderFactory, status_fulfilled=True)
    tracking_number = factory.Faker("pystr", min_chars=12, max_chars=25)


class ShipmentConfigFactory(DjangoModelFactory):
    class Meta:
        model = models.ShipmentConfig

    token = factory.Faker("pystr", min_chars=128, max_chars=128)


class FBAShipmentDestinationFactory(DjangoModelFactory):
    class Meta:
        model = models.FBAShipmentDestination

    name = factory.Faker("name")
    recipient_name = factory.Faker("name")
    contact_telephone = factory.Faker("phone_number")
    address_line_1 = factory.Faker("street_address")
    address_line_2 = factory.Faker("street_name")
    address_line_3 = factory.Faker("street_name")
    city = factory.Faker("city")
    state = factory.Faker("state")
    country = factory.Faker("country")
    country_iso = factory.Faker("country_code")
    postcode = factory.Faker("postcode")
    is_enabled = True


class FBAShipmentExportFactory(DjangoModelFactory):
    class Meta:
        model = models.FBAShipmentExport

    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )


class FBAShipmentMethodFactory(DjangoModelFactory):
    class Meta:
        model = models.FBAShipmentMethod

    name = factory.Faker("name")
    identifier = factory.Faker("name")
    priority = 0
    is_enabled = True


class FBAShipmentOrderFactory(DjangoModelFactory):
    class Meta:
        model = models.FBAShipmentOrder

    export = factory.SubFactory(FBAShipmentExportFactory)
    destination = factory.SubFactory(FBAShipmentDestinationFactory)
    shipment_method = factory.SubFactory(FBAShipmentMethodFactory)
    user = factory.SubFactory(UserFactory)
    is_on_hold = False
    at_risk = False
    planned_shipment_date = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )


class FBAShipmentPackageFactory(DjangoModelFactory):
    class Meta:
        model = models.FBAShipmentPackage

    shipment_order = factory.SubFactory(FBAShipmentOrderFactory)
    length_cm = factory.Faker("pyint", min_value=1, max_value=200)
    width_cm = factory.Faker("pyint", min_value=1, max_value=200)
    height_cm = factory.Faker("pyint", min_value=1, max_value=200)


class FBAShipmentItemFactory(DjangoModelFactory):
    class Meta:
        model = models.FBAShipmentItem

    package = factory.SubFactory(FBAShipmentPackageFactory)
    sku = factory.Faker("pystr", min_chars=9, max_chars=9)
    description = factory.Faker("sentence")
    quantity = factory.Faker("pyint", min_value=1, max_value=500)
    weight_kg = factory.Faker("pyfloat", positive=True, max_value=50, right_digits=2)
    value = 100
    country_of_origin = "United Kingdom"
    hr_code = factory.Faker("pystr", min_chars=25, max_chars=25)


class FBAProfitFileFactory(DjangoModelFactory):
    class Meta:
        model = models.FBAProfitFile

    import_date = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )


class FBAProfitFactory(DjangoModelFactory):
    class Meta:
        model = models.FBAProfit

    import_record = factory.SubFactory(FBAProfitFileFactory)
    product = factory.SubFactory(ProductFactory)
    region = factory.SubFactory(FBARegionFactory)
    last_order = factory.SubFactory(FBAOrderFactory)
    exchange_rate = 0.85
    channel_sku = "AAA_BBB_CCC_FBA"
    asin = "907083405"
    listing_name = factory.Faker("name")
    sale_price = factory.Faker("pyint", min_value=1, max_value=200)
    referral_fee = factory.Faker("pyint", min_value=1, max_value=200)
    closing_fee = factory.Faker("pyint", min_value=1, max_value=200)
    handling_fee = factory.Faker("pyint", min_value=1, max_value=200)
    placement_fee = factory.Faker("pyint", min_value=1, max_value=200)
    purchase_price = factory.Faker("pyint", min_value=1, max_value=200)
    shipping_price = factory.Faker("pyint", min_value=1, max_value=200)
    profit = factory.Faker("pyint", min_value=-200, max_value=200)
