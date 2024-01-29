"""Factories for the Purchases app."""

import datetime as dt
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from home.factories import StaffFactory
from inventory.factories import ProductFactory
from purchases import models
from shipping.factories import ShippingPriceFactory, ShippingServiceFactory


class PurchaseSettingsFactory(DjangoModelFactory):
    class Meta:
        model = models.PurchaseSettings

    purchase_charge = Decimal("1.30")
    send_report_to = factory.Faker("ascii_email")


class PurchaseExportFactory(DjangoModelFactory):
    class Meta:
        model = models.PurchaseExport

    export_date = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    report_sent = True


class PurchasableShippingServiceFactory(DjangoModelFactory):
    class Meta:
        model = models.PurchasableShippingService

    shipping_service = factory.SubFactory(ShippingServiceFactory)


class BasePurchaseFactory(DjangoModelFactory):
    class Meta:
        model = models.BasePurchase

    purchased_by = factory.SubFactory(StaffFactory)
    quantity = factory.Faker("pyint", min_value=1, max_value=10)
    export = factory.SubFactory(PurchaseExportFactory)
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    modified_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )


class ProductPurchaseFactory(BasePurchaseFactory):
    class Meta:
        model = models.ProductPurchase

    product = factory.SubFactory(ProductFactory)
    time_of_purchase_item_price = factory.Faker(
        "pydecimal", right_digits=2, positive=True, max_value=500, min_value=1
    )
    time_of_purchase_charge = factory.Faker(
        "pydecimal", right_digits=2, positive=True, max_value=500, min_value=1
    )


class ShippingPurchaseFactory(BasePurchaseFactory):
    class Meta:
        model = models.ShippingPurchase

    shipping_service = factory.SubFactory(ShippingPriceFactory)
    weight_grams = factory.Faker("pyint", min_value=50, max_value=2000)
    time_of_purchase_price = factory.Faker(
        "pydecimal", right_digits=2, positive=True, max_value=500, min_value=1
    )


class OtherPurchaseFactory(BasePurchaseFactory):
    class Meta:
        model = models.OtherPurchase

    description = factory.Faker("sentence")
    price = factory.Faker(
        "pydecimal", right_digits=2, positive=True, max_value=500, min_value=1
    )
