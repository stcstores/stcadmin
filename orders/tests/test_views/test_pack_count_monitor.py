from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed


@pytest.fixture
def url():
    return "/orders/pack_count_monitor/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


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
        assertTemplateUsed(valid_get_response, "orders/pack_count_monitor.html")
        is not False
    )


@pytest.fixture
def mock_now():
    with patch("orders.views.timezone.now") as mock_now:
        date_time = timezone.make_aware(datetime(2019, 12, 3, 11, 56, 23, 51))
        mock_now.return_value = date_time
        yield date_time


@pytest.fixture
def users(staff_factory):
    return [staff_factory.create() for _ in range(2)]


@pytest.fixture
def orders(users, mock_now, order_factory):
    [order_factory.create(dispatched_at=mock_now, packed_by=users[0]) for _ in range(2)]
    [order_factory.create(dispatched_at=mock_now, packed_by=users[1]) for _ in range(3)]


@pytest.fixture
def order_yesterday(mock_now, order_factory):
    order_factory.create(dispatched_at=mock_now - timedelta(days=1))


@pytest.fixture
def order_tomorrow(mock_now, order_factory):
    order_factory.create(dispatched_at=mock_now + timedelta(days=1))


@pytest.mark.django_db
def test_content(mock_now, users, orders, valid_get_response_content):
    assert valid_get_response_content == (
        "\n<tr>\n"
        f'    <th class="packer_name">{users[1].full_name()}</th>\n'
        '    <td class="packer_count">3</td>\n'
        "</tr>\n\n"
        "<tr>\n"
        f'    <th class="packer_name">{users[0].full_name()}</th>\n'
        '    <td class="packer_count">2</td>\n'
        "</tr>\n"
    )


@pytest.mark.django_db
def test_past_orders_are_not_displaid(
    mock_now, order_yesterday, valid_get_response_content
):
    assert valid_get_response_content == ""


@pytest.mark.django_db
def test_future_orders_are_not_displaid(
    mock_now, order_tomorrow, valid_get_response_content
):
    assert valid_get_response_content == ""
