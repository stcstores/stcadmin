"""Factories for the Purchases app."""
import datetime as dt
from decimal import Decimal

import factory
from factory import faker
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
    send_report_to = faker.Faker("ascii_email")


class PurchaseExportFactory(DjangoModelFactory):
    """Factory for purchases.PurchaseExport."""

    class Meta:
        """Meta class for PurchaseExportFactory."""

        model = models.PurchaseExport

    export_date = faker.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    report_sent = True


class PurchaseFactory(DjangoModelFactory):
    """Factory for purchases.Purchase."""

    class Meta:
        """Meta class for PurchaseFactory."""

        model = models.Purchase

    purchased_by = factory.SubFactory(StaffFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = faker.Faker("pyint", min_value=1, max_value=10)
    time_of_purchase_item_price = faker.Faker("pyint", min_value=100, max_value=1000)
    time_of_purchase_charge = Decimal("1.30")
    export = factory.SubFactory(PurchaseExportFactory)
    created_at = faker.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
    modified_at = faker.Faker(
        "date_time_this_decade", before_now=True, tzinfo=dt.timezone.utc
    )
