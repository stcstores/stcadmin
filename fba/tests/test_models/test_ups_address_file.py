from unittest import mock

import pytest

from fba.models import FBAShipmentOrder
from fba.models.shipment_files.ups_address_file import UPSAddressFile


@pytest.fixture
def shipment_export(fba_shipment_export_factory):
    return fba_shipment_export_factory.create()


@pytest.fixture
def shipment_orders(fba_shipment_order_factory, shipment_export):
    return fba_shipment_order_factory.create_batch(3, export=shipment_export)


@pytest.fixture
def shipment(fba_shipment_order_factory):
    return fba_shipment_order_factory.create()


@pytest.fixture
def shipment_items(fba_shipment_item_factory, fba_shipment_package_factory, shipment):
    packages = fba_shipment_package_factory.create_batch(2, shipment_order=shipment)
    return [
        fba_shipment_item_factory.create_batch(3, package=package)
        for package in packages
    ]


@pytest.mark.django_db
@mock.patch(
    "fba.models.shipment_files.ups_address_file.UPSAddressFile._create_address_row"
)
def test_create_rows_calls_create_address_row(
    mock_create_address_row, shipment_export, shipment_orders
):
    UPSAddressFile._create_rows(shipment_export)
    calls = [mock.call(shipment) for shipment in shipment_orders]
    mock_create_address_row.assert_has_calls(calls)


@pytest.mark.django_db
@mock.patch(
    "fba.models.shipment_files.ups_address_file.UPSAddressFile._create_address_row"
)
def test_create_rows_returns_rows(
    mock_create_address_row, shipment_export, shipment_orders
):
    return_value = UPSAddressFile._create_rows(shipment_export)
    assert return_value == [
        mock_create_address_row.return_value,
        mock_create_address_row.return_value,
        mock_create_address_row.return_value,
    ]


@pytest.mark.django_db
def test_create_address_row(shipment, shipment_items):
    shipment = FBAShipmentOrder.objects.get(pk=shipment.pk)
    row = UPSAddressFile._create_address_row(shipment)
    assert row == [
        shipment.destination.recipient_name,
        shipment.destination.address_line_1,
        shipment.destination.address_line_2,
        shipment.destination.address_line_3,
        shipment.destination.city,
        shipment.destination.state,
        shipment.destination.country,
        shipment.destination.postcode,
        shipment.destination.contact_telephone,
        "test@amazon.com",
        "TEST",
        "SHP",
        "REC",
        shipment.shipment_package.count(),
        str(round(shipment.weight_kg, 2)),
        "Package",
        "SV",
        str(shipment.order_number),
        "GBP",
        "WI-STC001",
    ]


@pytest.mark.django_db
@mock.patch("fba.models.shipment_files.ups_address_file.UPSAddressFile._create_rows")
def test_create_method(mock_create_rows, shipment_export):
    mock_create_rows.return_value = [[] * 5]
    return_value = UPSAddressFile.create(shipment_export)
    mock_create_rows.assert_called_once_with(shipment_export)
    assert isinstance(return_value, str)
