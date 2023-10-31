from unittest import mock

import pytest

from fba.models.shipment_files.ups_shipment_file import UPSShipmentFile


@pytest.fixture
def export(fba_shipment_export_factory):
    return fba_shipment_export_factory.create()


@pytest.fixture
def order(fba_shipment_order_factory, export):
    return fba_shipment_order_factory.create(export=export)


@pytest.fixture
def package(fba_shipment_package_factory, order):
    return fba_shipment_package_factory.create(shipment_order=order)


@pytest.fixture
def item(fba_shipment_item_factory, package):
    return fba_shipment_item_factory.create(package=package)


@pytest.fixture
def row_data(order, package, item):
    return {
        UPSShipmentFile.ORDER_NUMBER: order.order_number,
        UPSShipmentFile.PACKAGE_NUMBER: package.package_number,
        UPSShipmentFile.PACKAGE_LENGTH: package.length_cm,
        UPSShipmentFile.PACKAGE_WIDTH: package.width_cm,
        UPSShipmentFile.PACKAGE_HEIGHT: package.height_cm,
        UPSShipmentFile.PACKAGE_ITEM_DESCRIPTION: item.description.replace("'", ""),
        UPSShipmentFile.PACKAGE_ITEM_SKU: item.sku,
        UPSShipmentFile.PACKAGE_ITEM_WEIGHT: item.weight_kg,
        UPSShipmentFile.PACKAGE_ITEM_VALUE: str(float(item.value / 100)).format(
            "{:2f}"
        ),
        UPSShipmentFile.PACKAGE_ITEM_QUANTITY: item.quantity,
        UPSShipmentFile.PACKAGE_ITEM_COUNTRY_ORIGIN: item.country_of_origin,
        UPSShipmentFile.PACKAGE_ITEM_HARMONISATION_CODE: item.hr_code,
        UPSShipmentFile.ORDER_SHIPMENT_METHOD: "UPSES",
        UPSShipmentFile.PACKAGE_UNIT_OF_MEASURE: "EACH",
    }


@pytest.mark.django_db
def test_create_row_data(order, package, item, row_data):
    return_value = UPSShipmentFile._create_row_data(
        shipment_order=order, package=package, item=item
    )
    assert return_value == row_data


@pytest.mark.django_db
def test_calculate_total_weight(fba_shipment_export_factory, fba_shipment_item_factory):
    export = fba_shipment_export_factory.create()
    fba_shipment_item_factory.create_batch(
        5, package__shipment_order__export=export, weight_kg=5.0, quantity=2
    )
    assert UPSShipmentFile._calculate_total_weight(export) == 50.0


@pytest.mark.django_db
@mock.patch("fba.models.shipment_files.ups_shipment_file.UPSShipmentFile._create_rows")
def test_create_method(mock_create_rows, export):
    mock_create_rows.return_value = [[] * 5]
    return_value = UPSShipmentFile.create(export)
    mock_create_rows.assert_called_once_with(export)
    assert isinstance(return_value, str)


@mock.patch(
    "fba.models.shipment_files.ups_shipment_file.UPSShipmentFile._calculate_total_weight"
)
def test_get_total_row(mock_calculate_total_weight):
    mock_calculate_total_weight.return_value = 54.2569
    shipment = mock.Mock()
    returned_value = UPSShipmentFile._get_total_row(shipment)
    mock_calculate_total_weight.assert_called_once_with(shipment)
    assert len(returned_value) == len(UPSShipmentFile.HEADER)
    for i, value in enumerate(returned_value):
        if i == UPSShipmentFile.HEADER.index(UPSShipmentFile.PACKAGE_ITEM_WEIGHT):
            assert value == 54.257
        else:
            assert value is None


@mock.patch(
    "fba.models.shipment_files.ups_shipment_file.UPSShipmentFile._get_total_row"
)
@pytest.mark.django_db
def test_create_rows(mock_get_total_row, export, item, row_data):
    return_value = UPSShipmentFile._create_rows(export)
    mock_get_total_row.assert_called_once_with(export)
    assert return_value == [
        list(row_data.values()),
        mock_get_total_row.return_value,
    ]
