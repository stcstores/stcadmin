from unittest import mock

import pytest
from django.urls import reverse

from fba import models
from fba.views.api import ShipmentExports


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
    return reverse("fba:api_shipment_exports")


@pytest.fixture
def export(fba_shipment_export_factory):
    return fba_shipment_export_factory.create()


@pytest.fixture
def shipment(fba_shipment_order_factory, fba_shipment_item_factory, export):
    shipment = fba_shipment_order_factory.create(export=export)
    fba_shipment_item_factory.create(package__shipment_order=shipment)
    return shipment


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
def test_export_data(export, shipment):
    export = models.FBAShipmentExport.objects.first()
    value = ShipmentExports().export_data(export)
    assert value == {
        "id": export.id,
        "order_numbers": "\n".join(export.order_numbers()),
        "description": "\n".join(ShipmentExports()._export_description(export)),
        "destinations": "\n".join(export.destinations()),
        "shipment_count": export.shipment_count,
        "package_count": export.package_count,
        "created_at": export.created_at.strftime("%d %b %Y %H:%M"),
    }


@pytest.mark.django_db
@mock.patch("fba.views.api.models.FBAShipmentExport")
def test_get_exports(mock_model):
    value = ShipmentExports().get_exports()
    mock_model.objects.all.assert_called_once_with()
    mock_model.objects.all.return_value.order_by.assert_called_once_with("-created_at")
    assert (
        value
        == mock_model.objects.all.return_value.order_by.return_value[
            : ShipmentExports.EXPORT_LIMIT
        ]
    )


@pytest.mark.django_db
def test_export_description(fba_shipment_export_factory, fba_shipment_item_factory):
    export = fba_shipment_export_factory.create()
    descriptions = ["A" * 25, "B" * 25, "C" * 25]
    for description in descriptions:
        fba_shipment_item_factory.create(
            description=description, package__shipment_order__export=export
        )
    value = ShipmentExports()._export_description(export)
    assert sorted(value) == sorted(["A" * 20, "B" * 20, "C" * 20])


@pytest.mark.django_db
def test_returned_data(
    fba_shipment_export_factory,
    fba_shipment_order_factory,
    fba_shipment_item_factory,
    shipment_config,
    group_logged_in_client,
    url,
    form_data,
):
    export = fba_shipment_export_factory.create()
    shipments = fba_shipment_order_factory.create_batch(3, export=export)
    for shipment in shipments:
        fba_shipment_item_factory.create(package__shipment_order=shipment)
    response = group_logged_in_client.post(url, form_data)
    assert response.json() == {
        "exports": [
            ShipmentExports().export_data(export)
            for export in ShipmentExports().get_exports()
        ]
    }
