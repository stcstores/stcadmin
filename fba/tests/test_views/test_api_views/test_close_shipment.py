import pytest
from django.urls import reverse

from fba import models


@pytest.fixture
def token():
    return "suodghoi4h0298h309hg08h30h0st"


@pytest.fixture
def shipment_config(shipment_config_factory, token):
    return shipment_config_factory.create(token=token)


@pytest.fixture
def shipment(fba_shipment_order_factory):
    return fba_shipment_order_factory.create(export=None)


@pytest.fixture
def form_data(token, shipment):
    return {"token": token, "shipment_id": shipment.pk}


@pytest.fixture
def url():
    return reverse("fba:api_close_shipment")


@pytest.fixture
def post_response(shipment_config, group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


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
def test_closes_shipment_order(shipment, post_response):
    shipment.refresh_from_db()
    assert isinstance(shipment.export, models.FBAShipmentExport)


@pytest.mark.django_db
def test_response(shipment, post_response):
    shipment.refresh_from_db()
    assert post_response.json() == {"export_id": shipment.export.id}
