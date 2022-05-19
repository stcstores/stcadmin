from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed


@pytest.fixture
def url():
    return "/orders/undispatched_data/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def mock_now():
    with patch("django.utils.timezone.now") as mock_now:
        date_time = timezone.make_aware(datetime(2020, 2, 5, 16, 34, 11, 26))
        mock_now.return_value = date_time
        yield date_time


@pytest.fixture
def mock_urgent_since(mock_now):
    with patch("orders.models.order.urgent_since") as mock_urgent_since:
        date_time = mock_now - timedelta(days=2)
        mock_urgent_since.return_value = date_time
        yield date_time


@pytest.fixture
def urgent_orders(mock_urgent_since, order_factory):
    return [
        order_factory.create(
            recieved_at=mock_urgent_since - timedelta(hours=3), dispatched_at=None
        )
        for _ in range(3)
    ]


@pytest.fixture
def priority_orders(mock_now, order_factory):
    return [
        order_factory.create(
            shipping_service__priority=True,
            recieved_at=mock_now - timedelta(days=1),
            dispatched_at=None,
        )
        for _ in range(5)
    ]


@pytest.fixture
def non_priority_orders(mock_now, order_factory):
    return [
        order_factory.create(
            shipping_service__priority=False,
            recieved_at=mock_now - timedelta(days=1),
            dispatched_at=None,
        )
        for _ in range(5)
    ]


@pytest.fixture
def orders(urgent_orders, priority_orders, non_priority_orders):
    return urgent_orders + priority_orders + non_priority_orders


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


def test_logged_out_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 405


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 405


def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 405


def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(valid_get_response, "orders/undispatched_data.html")
        is not False
    )


@pytest.mark.django_db
def test_context_contains_urgent_orders(orders, urgent_orders, valid_get_response):
    order_ids = [order.order_id for order in urgent_orders]
    assert valid_get_response.context["urgent"] == order_ids


@pytest.mark.django_db
def test_context_contains_priority_orders(orders, priority_orders, valid_get_response):
    order_ids = [order.order_id for order in priority_orders]
    assert valid_get_response.context["priority"] == order_ids


@pytest.mark.django_db
def test_context_contains_non_priority_orders(
    orders, non_priority_orders, valid_get_response
):
    order_ids = [order.order_id for order in non_priority_orders]
    assert valid_get_response.context["non_priority"] == order_ids


@pytest.mark.django_db
def test_context_contains_total(orders, valid_get_response):
    assert valid_get_response.context["total"] == len(orders)


@pytest.mark.django_db
def test_order_ids_in_content(orders, valid_get_response_content):
    for order in orders:
        assert order.order_id in valid_get_response_content
