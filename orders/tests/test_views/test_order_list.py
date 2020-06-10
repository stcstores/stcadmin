from datetime import datetime
from unittest.mock import Mock

import pytest
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed

from orders import views


@pytest.fixture
def url():
    return "/orders/order_list/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(url, valid_get_request):
    return valid_get_request(url).content.decode("utf8")


@pytest.fixture
def order(order_factory):
    return order_factory.create()


def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 405


def test_uses_template(valid_get_response):
    assert assertTemplateUsed(valid_get_response, "orders/order_list.html") is not False


@pytest.mark.django_db
def test_shows_order_ID(order, valid_get_response_content):
    assert order.order_ID in valid_get_response_content


@pytest.mark.django_db
def test_shows_tracking_number(order, valid_get_response_content):
    assert order.tracking_number in valid_get_response_content


@pytest.mark.django_db
def test_shows_shipping_rule(order, valid_get_response_content):
    assert order.shipping_rule.name in valid_get_response_content


@pytest.mark.django_db
def test_shows_recieved_at(order, valid_get_response_content):
    assert order.recieved_at.strftime("%Y-%m-%d") in valid_get_response_content


@pytest.mark.django_db
def test_country_filter(country_factory, order_factory, url, group_logged_in_client):
    country = country_factory.create()
    order = order_factory.create(country=country)
    other_order = order_factory.create()
    response = group_logged_in_client.get(url, {"country": country.id})
    content = response.content.decode("utf8")
    assert order.order_ID in content
    assert other_order.order_ID not in content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "recieved_at,shown",
    [
        (datetime(2019, 12, 2, 23, 59), False),
        (datetime(2019, 12, 3, 0, 0), True),
        (datetime(2019, 12, 4, 23, 59), True),
        (datetime(2019, 12, 5, 0, 0), False),
    ],
)
def test_date_filter(recieved_at, shown, order_factory, url, group_logged_in_client):
    order = order_factory.create(recieved_at=timezone.make_aware(recieved_at))
    recieved_from = timezone.make_aware(datetime(2019, 12, 3))
    recieved_to = timezone.make_aware(datetime(2019, 12, 4))
    response = group_logged_in_client.get(
        url,
        {
            "recieved_from": recieved_from.strftime("%Y-%m-%d"),
            "recieved_to": recieved_to.strftime("%Y-%m-%d"),
        },
    )
    content = response.content.decode("utf8")
    assert (order.order_ID in content) is shown


@pytest.mark.django_db
def test_order_ID_filter(country_factory, order_factory, url, group_logged_in_client):
    order = order_factory.create()
    other_order = order_factory.create()
    response = group_logged_in_client.get(url, {"order_ID": order.order_ID})
    content = response.content.decode("utf8")
    assert order.order_ID in content
    assert other_order.order_ID not in content


def test_invalid_form(group_logged_in_client, url):
    response = group_logged_in_client.get(url, {"country": 999999})
    assert response.status_code == 200
    assert "country" in response.context["form"].errors


def test_page_range():
    paginator = Mock(num_pages=5)
    paginator.num_pages = 55
    page_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 55]
    assert views.OrderList().get_page_range(paginator) == page_numbers
