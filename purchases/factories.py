"""Factories for the Purchases app."""
import datetime

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from purchases import models
from shipping.tests.conftest import ShippingPriceFactory


class UserFactory(DjangoModelFactory):
    """Factory for the User model."""

    class Meta:
        """Meta class for the purchases.UserFactory model."""

        model = get_user_model()

    username = factory.Sequence(lambda n: "user_%d" % n)


class StockPurchaseFactory(DjangoModelFactory):
    """Factory for purchases.StockPurchaseFactory."""

    class Meta:
        """Meta class for the purchases.UserFactory model."""

        model = models.StockPurchase

    user = factory.SubFactory(UserFactory)
    created_at = datetime.datetime(2021, 5, 26, 10, 51, 36)
    created_by = factory.SubFactory(UserFactory)
    modified_at = datetime.datetime(2021, 5, 26, 10, 51, 36)
    to_pay = 1250
    cancelled = False
    product_id = "16846153"
    product_sku = "ABC-GHT-865"
    product_name = factory.sequence(lambda x: f"Test Product {x}")
    full_price = 2780
    discount_percentage = 20
    quantity = 5


class ShippingPurchaseFactory(DjangoModelFactory):
    """Factory for the purchases.ShippingPurchase model."""

    class Meta:
        """Meta class for purchases.ShippingPurchase."""

        model = models.ShippingPurchase

    user = factory.SubFactory(UserFactory)
    created_at = datetime.datetime(2021, 5, 26, 10, 51, 36)
    created_by = factory.SubFactory(UserFactory)
    modified_at = datetime.datetime(2021, 5, 26, 10, 51, 36)
    to_pay = 1250
    cancelled = False
    shipping_price = factory.SubFactory(ShippingPriceFactory)


class PurchaseNoteFactory(DjangoModelFactory):
    """Factory for the purchases.PurchaseNote model."""

    class Meta:
        """Meta class for purchases.PurchaseNoteFactory."""

        model = models.PurchaseNote

    user = factory.SubFactory(UserFactory)
    created_at = datetime.datetime(2021, 5, 26, 10, 51, 36)
    created_by = factory.SubFactory(UserFactory)
    modified_at = datetime.datetime(2021, 5, 26, 10, 51, 36)
    to_pay = 1250
    cancelled = False
    text = "Test purchase note text"
