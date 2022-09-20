import csv
import io
from datetime import datetime

import pytest
from django.utils import timezone


@pytest.fixture
def url():
    return "/orders/export_orders/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(url, valid_get_request):
    return valid_get_request(url).content.decode("utf8")


@pytest.fixture
def order(order_factory, product_sale_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order)
    return order


@pytest.fixture
def undispatched_order(order_factory, product_sale_factory):
    order = order_factory.create(dispatched_at=None)
    product_sale_factory.create(order=order)
    return order


@pytest.fixture
def export_rows():
    def _export_rows(response):
        return list(
            csv.reader(io.StringIO(response.content.decode("utf8")), delimiter=",")
        )

    return _export_rows


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


@pytest.mark.django_db
def test_export_contains_order(order, valid_get_response, export_rows):
    contents = export_rows(valid_get_response)
    assert contents[1] == [
        order.order_id,
        order.recieved_at.strftime("%Y-%m-%d"),
        order.dispatched_at.strftime("%Y-%m-%d"),
        order.country.name,
        order.channel.name,
        order.tracking_number,
        order.shipping_service.name,
        order.currency.code,
        f"{order.total_paid/100:.2f}",
        f"{order.total_paid_GBP/100:.2f}",
        str(order.total_weight()),
        f"{order.channel_fee_paid()/100:.2f}",
        f"{order.purchase_price()/100:.2f}",
        f"{order.profit()/100:.2f}",
        str(order.profit_percentage()),
    ]


@pytest.mark.django_db
def test_export_undispatched_order(undispatched_order, valid_get_response, export_rows):
    contents = export_rows(valid_get_response)
    assert contents[1] == [
        undispatched_order.order_id,
        undispatched_order.recieved_at.strftime("%Y-%m-%d"),
        "UNDISPATCHED",
        undispatched_order.country.name,
        undispatched_order.channel.name,
        undispatched_order.tracking_number,
        undispatched_order.shipping_service.name,
        undispatched_order.currency.code,
        f"{undispatched_order.total_paid/100:.2f}",
        f"{undispatched_order.total_paid_GBP/100:.2f}",
        str(undispatched_order.total_weight()),
        f"{undispatched_order.channel_fee_paid()/100:.2f}",
        f"{undispatched_order.purchase_price()/100:.2f}",
        f"{undispatched_order.profit()/100:.2f}",
        str(undispatched_order.profit_percentage()),
    ]


@pytest.mark.django_db
def test_country_filter(order_factory, url, group_logged_in_client, export_rows):
    order = order_factory.create()
    order_factory.create()
    response = group_logged_in_client.get(url, {"country": order.country.id})
    content = export_rows(response)
    assert content[1][0] == order.order_id
    assert len(content) == 2


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
def test_date_filter(
    recieved_at, shown, order_factory, url, group_logged_in_client, export_rows
):
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
    content = export_rows(response)
    if shown is True:
        assert content[1][0] == order.order_id
        assert len(content) == 2
    else:
        assert len(content) == 1


def test_invalid_form(url, group_logged_in_client):
    response = group_logged_in_client.get(url, {"country": 999999})
    assert response.status_code == 404
