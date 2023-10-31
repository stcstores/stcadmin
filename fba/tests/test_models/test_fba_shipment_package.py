import pytest

from fba import models


@pytest.fixture
def shipment_package(fba_shipment_package_factory):
    return fba_shipment_package_factory.create()


@pytest.mark.django_db
def test_full_clean(shipment_package):
    assert shipment_package.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_shipment_order_attribute(shipment_package):
    assert isinstance(shipment_package.shipment_order, models.FBAShipmentOrder)


@pytest.mark.django_db
def test_has_length_cm_attribute(shipment_package):
    assert isinstance(shipment_package.length_cm, int)


@pytest.mark.django_db
def test_has_width_cm_attribute(shipment_package):
    assert isinstance(shipment_package.width_cm, int)


@pytest.mark.django_db
def test_has_height_cm_attribute(shipment_package):
    assert isinstance(shipment_package.height_cm, int)


# Test Methods


@pytest.mark.django_db
def test_package_number_property(shipment_package):
    shipment_package.shipment_order.pk = 5
    shipment_package.pk = 3
    assert shipment_package.package_number == "STC_FBA_00005_3"


@pytest.mark.django_db
def test_str_method(shipment_package):
    shipment_package.shipment_order.pk = 5
    shipment_package.pk = 3
    assert str(shipment_package) == "FBA Shipment Order STC_FBA_00005 - STC_FBA_00005_3"


@pytest.mark.django_db
def test_description_method(fba_shipment_item_factory, shipment_package):
    descriptions = ["A", "B", "C"]
    for description in descriptions:
        fba_shipment_item_factory.create(
            package=shipment_package, description=description
        )
    assert shipment_package.description() == "A + 2 other items"


# Test Manager


@pytest.mark.django_db
def test_value_annotation(shipment_package, fba_shipment_item_factory):
    fba_shipment_item_factory.create(package=shipment_package, value=5, quantity=3)
    fba_shipment_item_factory.create(package=shipment_package, value=23, quantity=2)
    fba_shipment_item_factory.create(package=shipment_package, value=42, quantity=1)
    fba_shipment_item_factory.create(package=shipment_package, value=32, quantity=4)
    assert models.FBAShipmentPackage.objects.get(pk=shipment_package.pk).value == 231


@pytest.mark.django_db
def test_weight_kg_annotation(shipment_package, fba_shipment_item_factory):
    fba_shipment_item_factory.create(package=shipment_package, weight_kg=5, quantity=3)
    fba_shipment_item_factory.create(package=shipment_package, weight_kg=23, quantity=2)
    fba_shipment_item_factory.create(package=shipment_package, weight_kg=42, quantity=1)
    fba_shipment_item_factory.create(package=shipment_package, weight_kg=32, quantity=4)
    assert (
        models.FBAShipmentPackage.objects.get(pk=shipment_package.pk).weight_kg == 231
    )
