from datetime import datetime
from unittest.mock import Mock, patch

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


@pytest.fixture
def mock_now():
    with patch("django.utils.timezone.now") as mock_now:
        date_time = timezone.make_aware(datetime(2020, 3, 26))
        mock_now.return_value = date_time
        yield date_time


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
def test_shows_recieved_at(mock_now, order, valid_get_response_content):
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
def test_channel_filter(order_factory, channel_factory, url, group_logged_in_client):
    channel = channel_factory.create()
    order = order_factory.create(channel=channel)
    other_order = order_factory.create()
    response = group_logged_in_client.get(url, {"channel": channel.id})
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


@pytest.mark.django_db
def test_filter_status_any(order_factory, url, group_logged_in_client):
    orders = [
        order_factory.create(
            dispatched_at=timezone.make_aware(datetime(2019, 12, 4, 23, 59))
        ),
        order_factory.create(dispatched_at=None),
    ]
    response = group_logged_in_client.get(url, {"status": "any"})
    content = response.content.decode("utf8")
    for order in orders:
        assert order.order_ID in content


@pytest.mark.django_db
def test_filter_status_dispatched(order_factory, url, group_logged_in_client):
    orders = [
        order_factory.create(
            dispatched_at=timezone.make_aware(datetime(2019, 12, 4, 23, 59))
        ),
        order_factory.create(dispatched_at=None),
    ]
    response = group_logged_in_client.get(url, {"status": "dispatched"})
    content = response.content.decode("utf8")
    assert orders[0].order_ID in content
    assert orders[1].order_ID not in content


@pytest.mark.django_db
def test_filter_status_undispatched(order_factory, url, group_logged_in_client):
    orders = [
        order_factory.create(
            dispatched_at=timezone.make_aware(datetime(2019, 12, 4, 23, 59))
        ),
        order_factory.create(dispatched_at=None),
    ]
    response = group_logged_in_client.get(url, {"status": "undispatched"})
    content = response.content.decode("utf8")
    assert orders[1].order_ID in content
    assert orders[0].order_ID not in content


@pytest.mark.django_db
def test_filter_profit_calculable_only_true(
    order_factory, product_sale_factory, url, group_logged_in_client
):
    order = order_factory.create(postage_price_success=True)
    product_sale_factory.create(order=order, details_success=True)
    other_order = order_factory.create(postage_price_success=None)
    response = group_logged_in_client.get(url, {"profit_calculable_only": True})
    content = response.content.decode("utf8")
    assert order.order_ID in content
    assert other_order.order_ID not in content


@pytest.mark.django_db
def test_filter_profit_calculable_only_False(
    order_factory, url, group_logged_in_client
):
    order = order_factory.create(postage_price_success=None)
    other_order = order_factory.create(postage_price_success=True)
    response = group_logged_in_client.get(url, {"profit_calculable_only": False})
    content = response.content.decode("utf8")
    assert order.order_ID in content
    assert other_order.order_ID in content


@pytest.mark.django_db
def test_filter_contains_EOL_items_show(
    order_factory, product_sale_factory, url, group_logged_in_client
):
    order = order_factory.create()
    product_sale_factory.create(order=order, end_of_line=True)
    product_sale_factory.create(order=order, end_of_line=False)
    not_eol_order = order_factory.create()
    product_sale_factory.create(order=not_eol_order, end_of_line=False)
    unknown_eol_order = order_factory.create()
    product_sale_factory.create(order=unknown_eol_order, end_of_line=None)
    response = group_logged_in_client.get(url, {"contains_EOL_items": "show"})
    content = response.content.decode("utf8")
    assert order.order_ID in content
    assert not_eol_order.order_ID not in content
    assert unknown_eol_order.order_ID not in content


@pytest.mark.django_db
def test_filter_contains_EOL_items_hide(
    order_factory, product_sale_factory, url, group_logged_in_client
):
    order = order_factory.create()
    product_sale_factory.create(order=order, end_of_line=False)
    mixed_order = order_factory.create()
    product_sale_factory.create(order=mixed_order, end_of_line=True)
    product_sale_factory.create(order=mixed_order, end_of_line=False)
    eol_order = order_factory.create()
    product_sale_factory.create(order=eol_order, end_of_line=True)
    unknown_eol_order = order_factory.create()
    product_sale_factory.create(order=unknown_eol_order, end_of_line=None)
    response = group_logged_in_client.get(url, {"contains_EOL_items": "hide"})
    content = response.content.decode("utf8")
    assert order.order_ID in content
    assert mixed_order.order_ID not in content
    assert eol_order.order_ID not in content
    assert unknown_eol_order.order_ID not in content


def test_invalid_form(group_logged_in_client, url):
    response = group_logged_in_client.get(url, {"country": 999999})
    assert response.status_code == 200
    assert "country" in response.context["form"].errors


def test_page_range():
    paginator = Mock(num_pages=5)
    paginator.num_pages = 55
    page_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 55]
    assert views.OrderList().get_page_range(paginator) == page_numbers
