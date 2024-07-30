import datetime as dt

import pytest

from fba import models


@pytest.fixture
def shipment_export(fba_shipment_export_factory):
    return fba_shipment_export_factory.create()


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
