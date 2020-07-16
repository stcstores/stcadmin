import pytest
from pytest_django.asserts import assertTemplateUsed

from orders import models


@pytest.fixture
def refund(
    refund_factory, product_sale_factory, packing_record_factory, product_refund_factory
):
    refund = refund_factory.create()
    product = product_sale_factory.create(order=refund.order)
    packing_record_factory.create(order=refund.order)
    product_refund_factory.create(refund=refund, product=product)
    return refund


@pytest.fixture
def packing_record(refund):
    return models.PackingRecord.objects.get(order=refund.order)


@pytest.fixture
def other_product(product_sale_factory, refund):
    return product_sale_factory.create(order=refund.order)


@pytest.fixture
def url(db, refund):
    return f"/orders/refund/{refund.id}/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(url, valid_get_request):
    return valid_get_request(url).content.decode("utf8")


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
    assert (
        assertTemplateUsed(valid_get_response, "orders/refunds/refund.html")
        is not False
    )


def test_refund_in_context(valid_get_response, refund):
    assert valid_get_response.context["refund"] == refund


def test_order_in_context(valid_get_response, refund):
    assert valid_get_response.context["order"] == refund.order


def test_products_in_context(valid_get_response, refund):
    assert list(valid_get_response.context["products"]) == list(refund.products.all())


def test_other_products_in_context(valid_get_response, refund, other_product):
    assert list(valid_get_response.context["other_products"]) == [other_product]


def test_packing_record_in_context(valid_get_response, refund, packing_record):
    assert valid_get_response.context["packing_record"] == packing_record
