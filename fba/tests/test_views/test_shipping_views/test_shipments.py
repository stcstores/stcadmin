from unittest import mock

import pytest
from django.urls import reverse

from fba.views.shipping import Shipments


@pytest.fixture
def url():
    return reverse("fba:shipments")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "fba/shipments/shipments.html" in (t.name for t in get_response.templates)


@pytest.mark.django_db
def test_status_code(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.fixture
def mock_shipment_export_model():
    with mock.patch("fba.views.shipping.models.FBAShipmentExport") as m:
        yield m


@pytest.fixture
def mock_shipment_order_model():
    with mock.patch("fba.views.shipping.models.FBAShipmentOrder") as m:
        yield m


def test_previous_exports_in_context(
    mock_shipment_export_model, mock_shipment_order_model
):
    context = Shipments().get_context_data()
    mock_shipment_export_model.objects.all.assert_called_once_with()
    assert (
        context["previous_exports"]
        == mock_shipment_export_model.objects.all.return_value[:50]
    )


def test_current_shipments_in_context(
    mock_shipment_export_model, mock_shipment_order_model
):
    context = Shipments().get_context_data()
    mock_shipment_order_model.objects.filter.assert_called_once_with(
        export__isnull=True
    )
    mock_shipment_order_model.objects.filter.return_value.filter.assert_any_call(
        is_on_hold=False
    )
    assert (
        context["current_shipments"]
        == mock_shipment_order_model.objects.filter.return_value.filter.return_value
    )


def test_held_shipments_in_context(
    mock_shipment_export_model, mock_shipment_order_model
):
    context = Shipments().get_context_data()
    mock_shipment_order_model.objects.filter.assert_called_once_with(
        export__isnull=True
    )
    mock_shipment_order_model.objects.filter.return_value.filter.assert_called_with(
        is_on_hold=True
    )
    assert (
        context["held_shipments"]
        == mock_shipment_order_model.objects.filter.return_value.filter.return_value
    )
