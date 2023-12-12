import pytest
from django.urls import reverse


@pytest.fixture
def shipment_order(fba_shipment_order_factory):
    return fba_shipment_order_factory.create()


@pytest.fixture
def url(shipment_order):
    return reverse("fba:toggle_shipment_held", args=[shipment_order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_sets_shipment_on_hold(get_response, shipment_order):
    shipment_order.refresh_from_db()
    assert shipment_order.is_on_hold is True


@pytest.mark.django_db
def test_sets_on_hold_shipment_not_on_hold(group_logged_in_client, url, shipment_order):
    shipment_order.is_on_hold = True
    shipment_order.save()
    group_logged_in_client.get(url)
    shipment_order.refresh_from_db()
    assert shipment_order.is_on_hold is False


@pytest.mark.django_db
def test_redirect(get_response):
    assert get_response.status_code == 302
    assert get_response["Location"] == reverse("fba:shipments")
