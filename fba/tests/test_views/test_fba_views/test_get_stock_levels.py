import json
from unittest import mock

import pytest
from django.urls import reverse


@pytest.fixture
def orders(fba_order_factory):
    return fba_order_factory.create_batch(3, status_not_processed=True)


@pytest.fixture
def mock_stock_manager(orders):
    with mock.patch("fba.views.fba.StockManager") as m:
        m.get_stock_levels.return_value = {
            order.product.sku: mock.Mock(available=5, in_orders=1, stock_level=6)
            for order in orders
        }
        yield m


@pytest.fixture
def mock_base_product():
    with mock.patch("fba.views.fba.BaseProduct") as m:
        yield m


@pytest.fixture
def url(mock_stock_manager, mock_base_product):
    return reverse("fba:get_stock_levels")


def test_get_status_code(group_logged_in_client, url):
    assert group_logged_in_client.get(url).status_code == 405


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.fixture
def request_body(orders):
    return json.dumps({"order_ids": [order.id for order in orders]})


@pytest.fixture
def invalid_request_body():
    return "Invalid JSON"


@pytest.fixture
def post_response(group_logged_in_client, url, request_body):
    return group_logged_in_client.post(
        url, request_body, content_type="application/json"
    )


@pytest.mark.django_db
def test_calls_get_stock_levels(
    mock_stock_manager, mock_base_product, orders, post_response
):
    mock_base_product.objects.filter.assert_called_once_with(
        id__in=[order.product.id for order in orders]
    )
    mock_stock_manager.get_stock_levels.assert_called_once_with(
        mock_base_product.objects.filter.return_value
    )


@pytest.mark.django_db
def test_response(orders, post_response):
    assert post_response.json() == {
        str(order.id): {"available": 5, "in_orders": 1, "total": 6} for order in orders
    }


def test_invalid_item_form(group_logged_in_client, url, invalid_request_body):
    with pytest.raises(json.decoder.JSONDecodeError):
        group_logged_in_client.post(
            url, invalid_request_body, content_type="application/json"
        )
