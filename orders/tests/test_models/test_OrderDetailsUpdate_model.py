from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from orders import models


@pytest.fixture
def mock_now():
    with patch("orders.models.order_details_update.timezone.now") as mock_now:
        mock_now.return_value = timezone.make_aware(datetime(2020, 3, 1, 12, 36))
        yield mock_now.return_value


@pytest.fixture
def mock_update_product_details():
    with patch(
        "orders.models.order_details_update.OrderDetailsUpdate.objects._update_product_details"
    ) as mock_update_product_details:
        yield mock_update_product_details


@pytest.fixture
def completed_at():
    return timezone.make_aware(datetime(2020, 5, 1, 11, 36))


@pytest.fixture
def new_update():
    return models.OrderDetailsUpdate.objects.create()


@pytest.mark.django_db
def test_default_started_at(new_update):
    assert isinstance(new_update.started_at, datetime)


@pytest.mark.django_db
def test_default_completed_at(new_update):
    assert new_update.completed_at is None


@pytest.mark.django_db
def test_default_status(new_update):
    assert new_update.status == models.OrderDetailsUpdate.IN_PROGRESS


@pytest.mark.django_db
def test__str__method(order_details_update_factory):
    update = order_details_update_factory.create(
        status=models.OrderDetailsUpdate.IN_PROGRESS
    )
    assert (
        str(update)
        == f'OrderDetailsUpdate {update.started_at.strftime("%Y-%m-%d %H:%M:%S")} - In Progress'
    )


@pytest.mark.django_db
def test_mark_error(mock_now, order_details_update_factory):
    update = order_details_update_factory.create(
        status=models.OrderDetailsUpdate.IN_PROGRESS
    )
    update.mark_error()
    update.refresh_from_db()
    assert update.status == models.OrderDetailsUpdate.ERROR
    assert update.completed_at == mock_now


@pytest.mark.django_db
def test_mark_complete(mock_now, order_details_update_factory):
    update = order_details_update_factory.create(
        status=models.OrderDetailsUpdate.IN_PROGRESS
    )
    update.mark_complete()
    update.refresh_from_db()
    assert update.status == models.OrderDetailsUpdate.COMPLETE
    assert update.completed_at == mock_now


@pytest.mark.django_db
def test_details_update_updates_details(mock_update_product_details):
    models.OrderDetailsUpdate.objects.start_update()
    mock_update_product_details.assert_called_once()


@pytest.mark.django_db
def test_details_update_creates_order_update(mock_update_product_details):
    models.OrderDetailsUpdate.objects.start_update()
    assert models.OrderDetailsUpdate.objects.filter(
        status=models.OrderDetailsUpdate.COMPLETE, completed_at__isnull=False
    ).exists()


@pytest.mark.django_db
def test_details_update_raises_if_already_in_progress(
    mock_update_product_details, order_details_update_factory
):
    order_details_update_factory.create(status=models.OrderDetailsUpdate.IN_PROGRESS)
    with pytest.raises(models.OrderDetailsUpdate.OrderDetailsUpdateInProgressError):
        models.OrderDetailsUpdate.objects.start_update()


@pytest.mark.django_db
def test_details_update_marks_error_for_update_exception(mock_update_product_details):
    mock_update_product_details.side_effect = Exception()
    with pytest.raises(Exception):
        models.OrderDetailsUpdate.objects.start_update()
    assert models.OrderDetailsUpdate.objects.filter(
        status=models.OrderDetailsUpdate.ERROR, completed_at__isnull=False
    ).exists()


@pytest.mark.django_db
def test_timeout_update(mock_now, order_details_update_factory):
    update = order_details_update_factory.create(
        status=models.OrderDetailsUpdate.IN_PROGRESS
    )
    update.started_at = (
        mock_now - models.OrderDetailsUpdate.TIMEOUT - timedelta(minutes=1)
    )
    update.save()
    models.OrderDetailsUpdate.objects._timeout_update()
    update.refresh_from_db()
    assert update.status == models.OrderDetailsUpdate.ERROR


@pytest.mark.django_db
def test_timeout_does_not_change_completed_updates(
    mock_now, order_details_update_factory
):
    update = order_details_update_factory.create(
        status=models.OrderDetailsUpdate.COMPLETE
    )
    update.started_at = (
        mock_now - models.OrderDetailsUpdate.TIMEOUT - timedelta(minutes=1)
    )
    update.save()
    models.OrderDetailsUpdate.objects._timeout_update()
    update.refresh_from_db()
    assert update.status == models.OrderDetailsUpdate.COMPLETE


@pytest.mark.django_db
@patch("orders.models.order_details_update.OrderDetailsUpdate.objects._timeout_update")
def test_is_in_progress_timesout_updates(mock_timeout_update):
    models.OrderDetailsUpdate.objects.is_in_progress()
    mock_timeout_update.assert_called_once()


@pytest.mark.django_db
@patch("orders.models.order_details_update.OrderDetailsUpdate.objects._timeout_update")
def test_is_in_progress_returns_True_when_an_update_is_in_progress(
    mock_timeout_update, order_details_update_factory
):
    order_details_update_factory.create(status=models.OrderDetailsUpdate.IN_PROGRESS)
    assert models.OrderDetailsUpdate.objects.is_in_progress() is True


@pytest.mark.django_db
@patch("orders.models.order_details_update.OrderDetailsUpdate.objects._timeout_update")
def test_is_in_progress_returns_False_when_an_update_is_not_in_progress(
    mock_timeout_update,
):
    assert models.OrderDetailsUpdate.objects.is_in_progress() is False


@pytest.mark.django_db
@patch("orders.models.order_details_update.ProductSale.update_details")
def test_update_product_details(mock_update_details, product_sale_factory):
    product_sale_factory.create()
    models.OrderDetailsUpdate.objects.start_update()
    mock_update_details.assert_called_once()


@pytest.mark.django_db
@patch("orders.models.order_details_update.ProductSale.update_details")
def test_update_product_details_does_not_stop_for_errors(
    mock_update_details, product_sale_factory,
):
    mock_update_details.side_effect = Exception
    product_sale_factory.create()
    product_sale_factory.create()
    models.OrderDetailsUpdate.objects.start_update()
    assert len(mock_update_details.mock_calls) == 2


@pytest.mark.django_db
@patch("orders.models.order_details_update.ProductSale.update_details")
def test_update_creates_order_details_update_error_object(
    mock_update_details, product_sale_factory,
):
    error_text = "Exception Text"
    mock_update_details.side_effect = Exception(error_text)
    product_sale = product_sale_factory.create()
    models.OrderDetailsUpdate.objects.start_update()
    assert models.OrderDetailsUpdateError.objects.filter(
        product_sale=product_sale, text=error_text
    ).exists()
