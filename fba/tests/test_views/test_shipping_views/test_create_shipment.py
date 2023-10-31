import pytest
from django.contrib import messages
from django.urls import reverse

from fba.models import FBAShipmentOrder


@pytest.fixture
def destination(fba_shipment_destination_factory):
    return fba_shipment_destination_factory.create()


@pytest.fixture
def shipment_method(fba_shipment_method_factory):
    return fba_shipment_method_factory.create()


@pytest.fixture
def url(shipment_method, destination):
    return reverse("fba:create_shipment", args=[destination.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_redirects(get_response):
    shipment = FBAShipmentOrder.objects.first()
    assert get_response.status_code == 302
    assert get_response["Location"] == reverse(
        "fba:update_shipment", args=[shipment.pk]
    )


@pytest.mark.django_db
def test_creates_shipment(user, get_response, destination, shipment_method):
    assert FBAShipmentOrder.objects.filter(
        destination=destination, shipment_method=shipment_method, user=user
    ).exists()


@pytest.mark.django_db
def test_adds_message(group_logged_in_client, url):
    response = group_logged_in_client.get(url, follow=True)
    shipment = FBAShipmentOrder.objects.first()
    message = list(response.context["messages"])[0]
    assert message.message == f"Shipment {shipment.order_number} created."
    assert message.level == messages.SUCCESS
