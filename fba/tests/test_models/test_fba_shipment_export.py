import datetime as dt
from collections import Counter
from unittest import mock

import pytest

from fba import models


@pytest.fixture
def shipment_export(fba_shipment_export_factory):
    return fba_shipment_export_factory.create()


@pytest.fixture
def shipment_export_unsaved(fba_shipment_export_factory):
    return fba_shipment_export_factory.build()


@pytest.mark.django_db
def test_full_clean(shipment_export):
    assert shipment_export.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_created_at_attribute(shipment_export):
    assert isinstance(shipment_export.created_at, dt.datetime)


# Test Methods


def test_str_method(fba_shipment_export_factory):
    shipment_export = fba_shipment_export_factory.build(
        created_at=dt.datetime(2023, 1, 2)
    )
    assert str(shipment_export) == "FBA Shipment Export 2023-01-02"


@mock.patch("fba.models.shipments.UPSShipmentFile")
def test_generate_export_file(mock_ups_shipment_file, shipment_export_unsaved):
    return_value = shipment_export_unsaved.generate_export_file()
    mock_ups_shipment_file.assert_called_once_with()
    mock_ups_shipment_file.return_value.create.assert_called_once_with(
        shipment_export_unsaved
    )
    assert return_value == mock_ups_shipment_file.return_value.create.return_value


@mock.patch("fba.models.shipments.UPSAddressFile")
def test_generate_address_file(mock_ups_address_file, shipment_export_unsaved):
    return_value = shipment_export_unsaved.generate_address_file()
    mock_ups_address_file.create.assert_called_once_with(shipment_export_unsaved)
    assert return_value == mock_ups_address_file.create.return_value


@pytest.mark.django_db
def test_order_numbers_method(shipment_export, fba_shipment_order_factory):
    orders = fba_shipment_order_factory.create_batch(3, export=shipment_export)
    assert shipment_export.order_numbers() == [_.order_number for _ in orders]


@pytest.mark.django_db
def test_destinations_method(shipment_export, fba_shipment_order_factory):
    orders = fba_shipment_order_factory.create_batch(3, export=shipment_export)
    assert Counter(shipment_export.destinations()) == Counter(
        [_.destination.name for _ in orders]
    )


# Test Manager


@pytest.mark.django_db
def test_shipment_count_annotation(shipment_export, fba_shipment_order_factory):
    fba_shipment_order_factory.create_batch(5, export=shipment_export)
    export = models.FBAShipmentExport.objects.get(pk=shipment_export.pk)
    assert export.shipment_count == 5


@pytest.mark.django_db
def test_package_count_annotation(shipment_export, fba_shipment_package_factory):
    fba_shipment_package_factory.create_batch(5, shipment_order__export=shipment_export)
    export = models.FBAShipmentExport.objects.get(pk=shipment_export.pk)
    assert export.package_count == 5
