import pytest
from django.contrib import messages
from django.urls import reverse

from fba.forms import ShipmentOrderForm
from fba.models import FBAShipmentOrder


@pytest.fixture
def shipment(fba_shipment_order_factory):
    return fba_shipment_order_factory.create()


@pytest.fixture
def shipment_method(fba_shipment_method_factory):
    return fba_shipment_method_factory.create()


@pytest.fixture
def destination(fba_shipment_destination_factory):
    return fba_shipment_destination_factory.create()


@pytest.fixture
def form_data(destination, shipment_method, user):
    return {
        "destination": destination.id,
        "shipment_method": shipment_method.id,
        "user": user.id,
    }


@pytest.fixture
def url(shipment):
    return reverse("fba:update_shipment", args=[shipment.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "fba/shipments/create_shipment/update_shipment.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_get_response(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], ShipmentOrderForm)


@pytest.mark.django_db
def test_adds_message(group_logged_in_client, url, form_data):
    response = group_logged_in_client.post(url, form_data, follow=True)
    shipment = FBAShipmentOrder.objects.first()
    message = list(response.context["messages"])[0]
    assert message.message == f"Shipment {shipment.order_number} updated."
    assert message.level == messages.SUCCESS


@pytest.mark.django_db
def test_updates_shipment(
    group_logged_in_client, url, form_data, shipment, user, destination, shipment_method
):
    group_logged_in_client.post(url, form_data)
    shipment.refresh_from_db()
    assert shipment.user == user
    assert shipment.destination == destination
    assert shipment.shipment_method == shipment_method


@pytest.mark.django_db
def test_default_redirect(group_logged_in_client, url, form_data):
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 302
    assert response["Location"] == url


@pytest.mark.django_db
def test_redirect_to_new_package(group_logged_in_client, url, form_data, shipment):
    form_data["new_package"] = True
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 302
    assert response["Location"] == reverse("fba:create_package", args=[shipment.pk])


@pytest.mark.django_db
def test_redirect_to_edit_package(group_logged_in_client, url, form_data):
    form_data["edit_package"] = 2
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 302
    assert response["Location"] == reverse("fba:update_package", args=[2])


@pytest.mark.django_db
def test_redirect_to_delete_package(group_logged_in_client, url, form_data):
    form_data["delete_package"] = 2
    response = group_logged_in_client.post(url, form_data)
    assert response.status_code == 302
    assert response["Location"] == reverse("fba:delete_package", args=[2])
