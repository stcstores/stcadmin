import datetime as dt
from unittest import mock

import pytest
from django.contrib import messages
from django.urls import reverse
from django.utils.timezone import make_aware

from fba.models import FBAOrder
from fba.views.fba import RepeatFBAOrder


def test_max_duplicate_age_attribute():
    assert RepeatFBAOrder.MAX_DUPLICATE_AGE == dt.timedelta(days=30)


@pytest.fixture
def fba_order(fba_order_factory):
    return fba_order_factory.create(created_at=make_aware(dt.datetime.now()))


@pytest.fixture
def old_fba_order(fba_order_factory):
    return fba_order_factory.create(
        created_at=make_aware(dt.datetime.now() - dt.timedelta(days=31))
    )


@pytest.fixture
def mock_stock_manager():
    with mock.patch("fba.views.fba.StockManager") as m:
        yield m


@pytest.fixture
def url(mock_stock_manager, fba_order):
    return reverse("fba:repeat_order", args=[fba_order.pk])


@pytest.fixture
def old_order_url(mock_stock_manager, old_fba_order):
    return reverse("fba:repeat_order", args=[old_fba_order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_duplicate_order(mock_stock_manager):
    order = mock.Mock()
    RepeatFBAOrder().duplicate_order(order)
    mock_stock_manager.get_stock_level.assert_called_once_with(product=order.product)
    order.duplicate.assert_called_once_with(
        stock_level=mock_stock_manager.get_stock_level.return_value
    )


def test_redirect(get_response):
    assert get_response.status_code == 302
    assert get_response["Location"] == reverse("fba:order_list")


def test_adds_success_message(group_logged_in_client, url, fba_order):
    response = group_logged_in_client.get(url, follow=True)
    message = list(response.context["messages"])[0]
    assert message.message == f"Repeated FBA order {fba_order}."
    assert message.level == messages.SUCCESS


def test_adds_error_message(group_logged_in_client, old_order_url, old_fba_order):
    response = group_logged_in_client.get(old_order_url, follow=True)
    message = list(response.context["messages"])[0]
    assert message.message == f"FBA order {old_fba_order} is too old to be repeated."
    assert message.level == messages.ERROR


def test_duplicates_new_orders(get_response, fba_order):
    assert FBAOrder.objects.filter(product=fba_order.product).count() == 2


def test_does_not_duplicate_old_order(
    group_logged_in_client, old_order_url, old_fba_order
):
    group_logged_in_client.get(old_order_url)
    assert FBAOrder.objects.filter(product=old_fba_order.product).count() == 1
