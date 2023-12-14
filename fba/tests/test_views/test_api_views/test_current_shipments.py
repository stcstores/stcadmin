import pytest
from django.urls import reverse

from fba import models
from fba.views.api import CurrentShipments


@pytest.fixture
def token():
    return "suodghoi4h0298h309hg08h30h0st"


@pytest.fixture
def shipment_config(shipment_config_factory, token):
    return shipment_config_factory.create(token=token)


@pytest.fixture
def form_data(token):
    return {"token": token}


@pytest.fixture
def url():
    return reverse("fba:api_current_shipments")


@pytest.fixture
def shipment(fba_shipment_order_factory):
    return fba_shipment_order_factory.create()


@pytest.fixture
def items(fba_shipment_item_factory, shipment):
    return fba_shipment_item_factory.create_batch(3, package__shipment_order=shipment)


@pytest.mark.django_db
def test_request_from_user_not_in_group(shipment_config, url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_request_without_token(shipment_config, url, group_logged_in_client):
    response = group_logged_in_client.post(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_request_with_incorrect_token(shipment_config, url, group_logged_in_client):
    response = group_logged_in_client.post(url, {"token": "ihosdhfios"})
    assert response.status_code == 401


@pytest.mark.django_db
def test_shipment_data(shipment, items):
    shipment = models.FBAShipmentOrder.objects.first()
    value = CurrentShipments().shipment_data(shipment)
    assert value == {
        "id": shipment.id,
        "order_number": shipment.order_number,
        "description": shipment.description,
        "destination": shipment.destination.name,
        "user": str(shipment.user),
        "package_count": 3,
        "weight": round(shipment.weight_kg, 2),
        "value": f"£{shipment.value / 100:.2f}",
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "export,on_hold,package,expected",
    (
        (True, True, True, False),
        (True, True, False, False),
        (True, False, True, False),
        (True, False, False, False),
        (False, True, True, False),
        (False, True, False, False),
        (False, False, True, True),
        (False, False, False, False),
    ),
)
def test_get_shipments(
    export,
    on_hold,
    package,
    expected,
    fba_shipment_export_factory,
    fba_shipment_order_factory,
    fba_shipment_package_factory,
):
    export = fba_shipment_export_factory.create() if export else None
    shipment = fba_shipment_order_factory.create(export=export, is_on_hold=on_hold)
    if package:
        fba_shipment_package_factory.create(shipment_order=shipment)
    assert CurrentShipments().get_shipments().contains(shipment) is expected


@pytest.mark.django_db
def test_returned_data(
    fba_shipment_order_factory,
    fba_shipment_item_factory,
    shipment_config,
    group_logged_in_client,
    url,
    form_data,
):
    shipments = fba_shipment_order_factory.create_batch(3, export=None)
    for shipment in shipments:
        fba_shipment_item_factory.create(package__shipment_order=shipment)
    response = group_logged_in_client.post(url, form_data)
    assert response.json() == {
        "shipments": [
            CurrentShipments().shipment_data(shipment)
            for shipment in CurrentShipments().get_shipments()
        ]
    }
