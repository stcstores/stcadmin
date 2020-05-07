from datetime import datetime
from unittest.mock import Mock, patch

import factory
import pytest
import pytest_factoryboy
from django.utils import timezone

from itd import models
from shipping.models import Country, ShippingRule


@pytest.fixture
def mock_CCAPI():
    with patch("itd.models.CCAPI") as mock_CCAPI:
        yield mock_CCAPI


@pytest.fixture
def mock_orders(mock_CCAPI):
    mock_products = [
        Mock(
            sku="ABC-DEF-GHI",
            product_name="Order Product 1",
            price=34.56,
            per_item_weight=255.10,
            quantity=3,
        ),
        Mock(
            sku="JKL-MNO-OPQ",
            product_name="Order Product 2",
            price=12.56,
            per_item_weight=150.5,
            quantity=1,
        ),
    ]
    mock_order = Mock(
        order_id="3893038",
        customer_id="284938403",
        delivery_name="Joe Bloggs",
        products=mock_products,
        delilvery_address="123 No Road\tNowhere,Sometown,Someplace,EB23 2BD",
        delivery_country_code="1",
    )
    mock_orders = [mock_order]
    mock_CCAPI.get_orders_for_dispatch.return_value = [mock_order]
    return mock_orders


@pytest.fixture
def mock_now():
    with patch("django.utils.timezone.now") as mock_now:
        mock_now.return_value = timezone.make_aware(datetime(2020, 4, 19, 15, 47, 25))
        yield mock_now.return_value


@pytest_factoryboy.register
class ItdManifestFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ITDManifest

    created_at = timezone.make_aware(datetime(2020, 3, 24, 11, 19))
    last_generated_at = timezone.make_aware(datetime(2020, 3, 24, 15, 57))
    status = models.ITDManifest.OPEN


@pytest_factoryboy.register
class ItdOrderFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ITDOrder

    manifest = factory.SubFactory(ItdManifestFactory)
    order_id = factory.Sequence(lambda n: f"1568616161{n}")
    customer_id = factory.Sequence(lambda n: f"681164866{n}")


@pytest_factoryboy.register
class ItdProductFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.ITDProduct

    order = factory.SubFactory(ItdOrderFactory)
    sku = factory.Sequence(lambda n: f"ABC-DEF-12{n}")
    name = factory.Sequence(lambda n: f"Order Product {n}")
    weight = 210
    price = 3472
    quantity = 1


@pytest_factoryboy.register
class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Country

    country_ID = 1
    name = "United Kingdom"


@pytest_factoryboy.register
class ShippingRuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = ShippingRule

    rule_ID = factory.Sequence(lambda n: str(1008 + n))
    name = factory.Sequence(lambda n: f"Shipping Rule {n}")
    priority = False
    inactive = False
