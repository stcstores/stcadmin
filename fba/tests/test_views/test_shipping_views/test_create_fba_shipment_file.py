import pytest
from django.urls import reverse


@pytest.fixture
def shipment_order(fba_shipment_order_factory):
    return fba_shipment_order_factory.create(export=None)


@pytest.fixture
def url(shipment_order):
    return reverse("fba:create_shipment_file", args=[shipment_order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_redirects(get_response):
    assert get_response.status_code == 302
    assert get_response["Location"] == reverse("fba:shipments")


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_closes_shipment_order(shipment_order, get_response):
    shipment_order.refresh_from_db()
    assert shipment_order.export is not None
