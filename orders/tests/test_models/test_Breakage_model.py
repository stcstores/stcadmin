from datetime import datetime
from unittest.mock import patch

import pytest
from django.utils import timezone

from orders import models


@pytest.fixture
def mock_now():
    with patch("orders.models.breakage.timezone.now") as mock_now:
        mock_time = timezone.make_aware(datetime(2020, 5, 23, 12, 53, 29))
        mock_now.return_value = mock_time
        yield mock_time


@pytest.fixture
def product_sku():
    return "ABC-123-DEF"


@pytest.fixture
def order_id():
    return "38493038"


@pytest.fixture
def packer(cloud_commerce_user_factory):
    return cloud_commerce_user_factory.create()


@pytest.fixture
def new_breakage(product_sku, order_id, packer):
    breakage = models.Breakage(
        product_sku=product_sku, order_id=order_id, packer=packer
    )
    breakage.save()
    return breakage


@pytest.mark.django_db
def test_sets_product_sku(new_breakage, product_sku):
    assert new_breakage.product_sku == product_sku


@pytest.mark.django_db
def test_sets_order_id(new_breakage, order_id):
    assert new_breakage.order_id == order_id


@pytest.mark.django_db
def test_sets_note(new_breakage):
    assert new_breakage.note is None


@pytest.mark.django_db
def test_can_set_note(product_sku, order_id, packer):
    note = "some text"
    breakage = models.Breakage(
        product_sku=product_sku, order_id=order_id, packer=packer, note=note
    )
    breakage.save()
    breakage.refresh_from_db()
    assert breakage.note == note


@pytest.mark.django_db
def test_sets_packer(new_breakage, packer):
    assert new_breakage.packer == packer


@pytest.mark.django_db
def test_sets_timestamp(mock_now, new_breakage):
    assert new_breakage.timestamp == mock_now


@pytest.mark.django_db
def test__str__method(breakage_factory):
    breakage = breakage_factory.create(product_sku="ABC-DEF-123", order_id="897345")
    assert str(breakage) == "ABC-DEF-123 on order 897345"


@pytest.mark.django_db
def test_ordering(breakage_factory):
    breakages = sorted(
        [breakage_factory.create() for _ in range(5)], key=lambda x: x.timestamp
    )
    assert list(models.Breakage.objects.all()) == breakages
