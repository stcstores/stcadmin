from unittest.mock import Mock, patch

import pytest

from home.models import CloudCommerceUser
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


@pytest.fixture
def mock_CCAPI():
    with patch("orders.models.packing_record.CCAPI") as mock_CCAPI:
        yield mock_CCAPI


@pytest.fixture
def mock_customer_log(mock_CCAPI, order, packed_by):
    mock_log = Mock(
        note=(
            "Order Dispatched - Date: 05/12/2019 11:08:51 "
            f"OrderID: {order.order_ID} Override: No"
        ),
        added_by_user_ID=packed_by.user_id,
    )
    mock_CCAPI.customer_logs.return_value = [mock_log]


@pytest.fixture
def mock_invalid_customer_log(mock_CCAPI, order):
    mock_log = Mock(
        note=(
            "Some Other Note - Date: 05/12/2019 11:08:51 "
            f"OrderID: {order.order_ID} Override: No"
        ),
        added_by_user_ID="4859483",
    )
    mock_CCAPI.customer_logs.return_value = [mock_log]


@pytest.mark.django_db
def test_sets_order(new_packing_record, order):
    assert new_packing_record.order == order


@pytest.mark.django_db
def test_sets_packed_by(new_packing_record, packed_by):
    assert new_packing_record.packed_by == packed_by


@pytest.mark.django_db
def test_update_packing_records_creates_packing_record(
    mock_customer_log, order, packed_by
):
    models.PackingRecord.objects.update_packing_records()
    assert models.PackingRecord.objects.filter(
        order=order, packed_by=packed_by
    ).exists()


@pytest.mark.django_db
def test_update_packing_records_requests_customer_logs(
    mock_CCAPI, mock_customer_log, order
):
    models.PackingRecord.objects.update_packing_records()
    mock_CCAPI.customer_logs.assert_called_once_with(order.customer_ID)


@pytest.mark.django_db
def test_orders_to_update_method(order_factory):
    dispatched_orders = [order_factory.create() for _ in range(3)]
    [order_factory.create(dispatched_at=None) for _ in range(3)]  # Undispatched orders
    orders = models.PackingRecord.objects._orders_to_update()
    assert set(orders) == set(dispatched_orders)


@pytest.mark.django_db
def test_orders_to_update_ignores_null_customer_ID(order_factory):
    incomplete_order = order_factory.create(customer_ID=None)
    [order_factory.create() for _ in range(3)]
    result = models.PackingRecord.objects._orders_to_update()
    assert incomplete_order not in result


@pytest.mark.django_db
def test_orders_to_update_ignores_existing_records(
    order_factory, packing_record_factory
):
    order = order_factory.create()
    packing_record_factory.create(order=order)
    result = models.PackingRecord.objects._orders_to_update()
    assert list(result) == []


@pytest.mark.django_db
def test_update_order_with_no_logs(mock_CCAPI, order_factory):
    mock_CCAPI.customer_logs.return_value = []
    models.PackingRecord.objects._update_order(order_factory.create())
    assert models.PackingRecord.objects.exists() is False


@pytest.mark.django_db
def test_order_update_with_no_dispatch_logs(order, mock_invalid_customer_log):
    models.PackingRecord.objects._update_order(order)
    assert models.PackingRecord.objects.exists() is False


@pytest.mark.django_db
def test_update_order_with_new_packer(mock_CCAPI, order):
    new_user_ID = "32940383"
    mock_log = Mock(
        note=(
            "Order Dispatched - Date: 05/12/2019 11:08:51 "
            f"OrderID: {order.order_ID} Override: No"
        ),
        added_by_user_ID=new_user_ID,
    )
    mock_CCAPI.customer_logs.return_value = [mock_log]
    models.PackingRecord.objects._update_order(order)
    assert CloudCommerceUser.objects.filter(user_id=new_user_ID).exists() is True
