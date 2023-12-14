from unittest import mock

import pytest
from django.urls import reverse

from fba.views.fba import FBAOrderPrintout


def test_template_name_attribute():
    assert FBAOrderPrintout.template_name == "fba/order_printout.html"


@pytest.fixture
def mock_stock_manager():
    with mock.patch("fba.views.fba.StockManager") as m:
        yield m


@pytest.fixture
def stock_level_info_error(mock_stock_manager):
    mock_stock_manager.stock_level_info.side_effect = Exception


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_not_processed=True)


@pytest.fixture
def bays(order, product_bay_link_factory):
    links = product_bay_link_factory.create_batch(3, product=order.product)
    return [link.bay for link in links]


@pytest.fixture
def url(mock_stock_manager, order):
    return reverse("fba:order_printout", args=[order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response):
    assert "fba/order_printout.html" in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_order_in_context(get_response, order):
    assert get_response.context["order"] == order


def test_product_in_context(get_response, order):
    assert get_response.context["product"] == order.product


def test_calls_stock_level_info(get_response, order, mock_stock_manager):
    mock_stock_manager.stock_level_info.assert_called_once_with(order.product.sku)


def test_stock_level_in_context(get_response, mock_stock_manager):
    expected = mock_stock_manager.stock_level_info.return_value.stock_level
    assert get_response.context["stock_level"] == expected


def test_pending_stock_in_context(get_response, mock_stock_manager):
    expected = mock_stock_manager.stock_level_info.return_value.in_orders
    assert get_response.context["pending_stock"] == expected


def test_stock_level_with_error(
    mock_stock_manager, stock_level_info_error, get_response
):
    assert get_response.context["stock_level"] == "ERROR"


def test_pending_stock_with_error(
    mock_stock_manager, stock_level_info_error, get_response
):
    assert get_response.context["pending_stock"] == "ERROR"


@pytest.mark.django_db
def test_bays_in_context(bays, get_response):
    for bay in bays:
        assert bay.name in get_response.context["bays"]


def test_sets_order_printed(get_response, order):
    order.refresh_from_db()
    assert order.printed is True
