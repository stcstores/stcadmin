from unittest import mock

import pytest
from django.urls import reverse

from fba.views.shipping import CreateShipment_SelectDestination


@pytest.fixture
def url():
    return reverse("fba:create_shipment_select_destination")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "fba/shipments/create_shipment/select_destination.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_status_code(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.fixture
def mock_shipment_destinaion_model():
    with mock.patch("fba.views.shipping.models.FBAShipmentDestination") as m:
        yield m


def test_destinations_in_context(mock_shipment_destinaion_model):
    context = CreateShipment_SelectDestination().get_context_data()
    mock_shipment_destinaion_model.objects.filter.assert_called_once_with(
        is_enabled=True
    )
    assert (
        context["destinations"]
        == mock_shipment_destinaion_model.objects.filter.return_value
    )
