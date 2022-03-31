import pytest

from orders import models


@pytest.fixture
def order(order_factory):
    return order_factory.create()


@pytest.fixture
def packed_by(cloud_commerce_user_factory):
    return cloud_commerce_user_factory.create()


@pytest.fixture
def new_packing_record(order, packed_by):
    packing_record = models.PackingRecord(order=order, packed_by=packed_by)
    packing_record.save()
    return packing_record


@pytest.mark.django_db
def test_sets_order(new_packing_record, order):
    assert new_packing_record.order == order


@pytest.mark.django_db
def test_sets_packed_by(new_packing_record, packed_by):
    assert new_packing_record.packed_by == packed_by
