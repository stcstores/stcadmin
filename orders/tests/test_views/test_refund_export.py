import csv
import io

import pytest


@pytest.fixture
def url():
    return "/orders/export_refunds/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(url, valid_get_request):
    return valid_get_request(url).content.decode("utf8")


@pytest.fixture
def refund(refund_factory, product_refund_factory):
    refund = refund_factory.create()
    product_refund_factory.create(refund=refund)
    return refund


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
def test_export_contains_refund(refund, valid_get_response, export_rows):
    contents = export_rows(valid_get_response)
    assert contents[1] == [
        refund.order.order_ID,
        refund.reason(),
        refund.order.recieved_at.strftime("%Y-%m-%d"),
        refund.order.dispatched_at.strftime("%Y-%m-%d"),
        refund.order.country.name,
        refund.order.channel.name,
        refund.order.tracking_number,
        "",
        "",
        "",
        "",
        "",
    ]


@pytest.mark.django_db
def test_export_contains_courier_refund(
    url,
    export_rows,
    lost_in_post_refund_factory,
    product_refund_factory,
    group_logged_in_client,
):
    refund = lost_in_post_refund_factory.create()
    product_refund_factory.create(refund=refund)
    response = group_logged_in_client.get(url)
    contents = export_rows(response)
    assert contents[1] == [
        refund.order.order_ID,
        refund.reason(),
        refund.order.recieved_at.strftime("%Y-%m-%d"),
        refund.order.dispatched_at.strftime("%Y-%m-%d"),
        refund.order.country.name,
        refund.order.channel.name,
        refund.order.tracking_number,
        refund.courier.name,
        "",
        str(refund.contact_contacted),
        "",
        f"{refund.refund_amount / 100:.2f}",
    ]


@pytest.mark.django_db
def test_export_contains_supplier_refund(
    url,
    export_rows,
    breakage_refund_factory,
    product_refund_factory,
    group_logged_in_client,
):
    refund = breakage_refund_factory.create()
    product_refund_factory.create(refund=refund)
    response = group_logged_in_client.get(url)
    contents = export_rows(response)
    assert contents[1] == [
        refund.order.order_ID,
        refund.reason(),
        refund.order.recieved_at.strftime("%Y-%m-%d"),
        refund.order.dispatched_at.strftime("%Y-%m-%d"),
        refund.order.country.name,
        refund.order.channel.name,
        refund.order.tracking_number,
        "",
        refund.supplier.name,
        str(refund.contact_contacted),
        "",
        f"{refund.refund_amount / 100:.2f}",
    ]
