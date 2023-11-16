"""Factories for the Purchases app."""
import datetime as dt
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from home.factories import StaffFactory
from inventory.factories import ProductFactory
from purchases import models


class PurchaseSettingsFactory(DjangoModelFactory):
    """Factory for purchases.PurchaseSettings."""

    class Meta:
        """Meta class PurchaseSettingsFactory."""

        model = models.PurchaseSettings

    purchase_charge = Decimal("1.30")
    send_report_to = factory.Faker("ascii_email")


class PurchaseExportFactory(DjangoModelFactory):
    """Factory for purchases.PurchaseExport."""

    class Meta:
        """Meta class for PurchaseExportFactory."""

        model = models.PurchaseExport

    export_date = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    created_at = factory.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    report_sent = True


class BasePurchaseFactory(DjangoModelFactory):
    """Factory for purchases.BasePurchase."""

    class Meta:
        """Meta class for BasePurchaseFactory."""

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
    """Factory for purchases.ProductPurchase."""

    class Meta:
        """Meta class for ProductPurchaseFactory."""

        model = models.ProductPurchase

    product = factory.SubFactory(ProductFactory)
    time_of_purchase_item_price = factory.Faker("pyint", min_value=100, max_value=1000)
    time_of_purchase_charge = Decimal("1.30")
