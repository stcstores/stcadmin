from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from orders import models


@pytest.fixture
def mock_now():
    with patch("orders.models.update.timezone.now") as mock_now:
        mock_now.return_value = timezone.make_aware(datetime(2020, 3, 1, 12, 36))
        yield mock_now.return_value


@pytest.fixture
def mock_update_orders():
    with patch(
        "orders.models.update.Order.objects.update_orders"
    ) as mock_update_orders:
        yield mock_update_orders


@pytest.fixture
def mock_update_packing_records():
    with patch(
        "orders.models.update.PackingRecord.objects.update_packing_records"
    ) as mock_update_packing_records:
        yield mock_update_packing_records


@pytest.fixture
def completed_at():
    return timezone.make_aware(datetime(2020, 5, 1, 11, 36))


@pytest.fixture
def new_update():
    return models.OrderUpdate.objects.create()


@pytest.mark.django_db
def test_default_started_at(new_update):
    assert isinstance(new_update.started_at, datetime)


@pytest.mark.django_db
def test_default_completed_at(new_update):
    assert new_update.completed_at is None


@pytest.mark.django_db
def test_default_status(new_update):
    assert new_update.status == models.OrderUpdate.IN_PROGRESS


@pytest.mark.django_db
def test__str__method(order_update_factory):
    update = order_update_factory.create(status=models.OrderUpdate.IN_PROGRESS)
    assert (
        str(update)
        == f'OrderUpdate {update.started_at.strftime("%Y-%m-%d %H:%M:%S")} - In Progress'
    )


@pytest.mark.django_db
def test_mark_error(mock_now, order_update_factory):
    update = order_update_factory.create(status=models.OrderUpdate.IN_PROGRESS)
    update.mark_error()
    update.refresh_from_db()
    assert update.status == models.OrderUpdate.ERROR
    assert update.completed_at == mock_now


@pytest.mark.django_db
def test_mark_complete(mock_now, order_update_factory):
    update = order_update_factory.create(status=models.OrderUpdate.IN_PROGRESS)
    update.mark_complete()
    update.refresh_from_db()
    assert update.status == models.OrderUpdate.COMPLETE
    assert update.completed_at == mock_now


@pytest.mark.django_db
def test_order_update_updates_orders(mock_update_orders, mock_update_packing_records):
    models.OrderUpdate.objects.start_order_update()
    mock_update_orders.assert_called_once()


@pytest.mark.django_db
def test_order_update_updates_packing_records(
    mock_update_orders, mock_update_packing_records
):
    models.OrderUpdate.objects.start_order_update()
    mock_update_packing_records.assert_called_once()


@pytest.mark.django_db
def test_order_update_creates_order_update(
    mock_update_orders, mock_update_packing_records
):
    models.OrderUpdate.objects.start_order_update()
    assert models.OrderUpdate.objects.filter(
        status=models.OrderUpdate.COMPLETE, completed_at__isnull=False
    ).exists()


@pytest.mark.django_db
def test_order_update_raises_if_already_in_progress(
    mock_update_orders, mock_update_packing_records, order_update_factory
):
    order_update_factory.create(status=models.OrderUpdate.IN_PROGRESS)
    with pytest.raises(models.OrderUpdate.OrderUpdateInProgressError):
        models.OrderUpdate.objects.start_order_update()


@pytest.mark.django_db
def test_order_update_marks_error_for_update_exception(
    mock_update_orders, mock_update_packing_records
):
    mock_update_orders.side_effect = Exception()
    with pytest.raises(Exception):
        models.OrderUpdate.objects.start_order_update()
    assert models.OrderUpdate.objects.filter(
        status=models.OrderUpdate.ERROR, completed_at__isnull=False
    ).exists()


@pytest.mark.django_db
def test_order_update_marks_error_for_packing_record_exception(
    mock_update_orders, mock_update_packing_records
):
    mock_update_packing_records.side_effect = Exception()
    with pytest.raises(Exception):
        models.OrderUpdate.objects.start_order_update()
    assert models.OrderUpdate.objects.filter(
        status=models.OrderUpdate.ERROR, completed_at__isnull=False
    ).exists()


@pytest.mark.django_db
def test_timeout_update(mock_now, order_update_factory):
    update = order_update_factory.create(status=models.OrderUpdate.IN_PROGRESS)
    update.started_at = mock_now - models.OrderUpdate.TIMEOUT - timedelta(minutes=1)
    update.save()
    models.OrderUpdate.objects._timeout_update()
    update.refresh_from_db()
    assert update.status == models.OrderUpdate.ERROR


@pytest.mark.django_db
def test_timeout_does_not_change_completed_updates(mock_now, order_update_factory):
    update = order_update_factory.create(status=models.OrderUpdate.COMPLETE)
    update.started_at = mock_now - models.OrderUpdate.TIMEOUT - timedelta(minutes=1)
    update.save()
    models.OrderUpdate.objects._timeout_update()
    update.refresh_from_db()
    assert update.status == models.OrderUpdate.COMPLETE


@pytest.mark.django_db
@patch("orders.models.update.OrderUpdate.objects._timeout_update")
def test_is_in_progress_timesout_updates(mock_timeout_update):
    models.OrderUpdate.objects.is_in_progress()
    mock_timeout_update.assert_called_once()


@pytest.mark.django_db
@patch("orders.models.update.OrderUpdate.objects._timeout_update")
def test_is_in_progress_returns_True_when_an_update_is_in_progress(
    mock_timeout_update, order_update_factory
):
    order_update_factory.create(status=models.OrderUpdate.IN_PROGRESS)
    assert models.OrderUpdate.objects.is_in_progress() is True


@pytest.mark.django_db
@patch("orders.models.update.OrderUpdate.objects._timeout_update")
def test_is_in_progress_returns_False_when_an_update_is_not_in_progress(
    mock_timeout_update,
):
    assert models.OrderUpdate.objects.is_in_progress() is False
