import pytest
from django.contrib.auth import get_user_model

from fba import models


@pytest.fixture
def shipment_order(fba_shipment_order_factory):
    return fba_shipment_order_factory.create()


@pytest.mark.django_db
def test_full_clean(shipment_order):
    assert shipment_order.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_export_attribute(shipment_order):
    assert isinstance(shipment_order.export, models.FBAShipmentExport)


@pytest.mark.django_db
def test_has_destination_attribute(shipment_order):
    assert isinstance(shipment_order.destination, models.FBAShipmentDestination)


@pytest.mark.django_db
def test_has_shipment_method_attribute(shipment_order):
    assert isinstance(shipment_order.shipment_method, models.FBAShipmentMethod)


@pytest.mark.django_db
def test_has_user_attribute(shipment_order):
    assert isinstance(shipment_order.user, get_user_model())


@pytest.mark.django_db
def test_has_is_on_hold_attribute(shipment_order):
    assert shipment_order.is_on_hold is False


# Test Methods


@pytest.mark.django_db
def test_str_method(shipment_order):
    assert str(shipment_order) == "FBA Shipment Order STC_FBA_" + str(
        shipment_order.pk
    ).zfill(5)


@pytest.mark.django_db
def test_order_number_property(shipment_order):
    assert shipment_order.order_number == "STC_FBA_" + str(shipment_order.pk).zfill(5)


@pytest.mark.django_db
def test_description_property(fba_shipment_item_factory, shipment_order):
    descriptions = ["A", "B", "C"]
    for description in descriptions:
        fba_shipment_item_factory.create(
            package__shipment_order=shipment_order, description=description
        )
    assert shipment_order.description == "A + 2 other items"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "export,is_on_hold,shipment_package,expected",
    (
        (False, False, False, False),
        (True, False, False, False),
        (False, True, False, False),
        (True, True, False, False),
        (False, False, True, True),
        (True, False, True, False),
        (False, True, True, False),
        (True, True, True, False),
    ),
)
def test_is_shippable_property(
    export,
    is_on_hold,
    shipment_package,
    expected,
    fba_shipment_order_factory,
    fba_shipment_package_factory,
    fba_shipment_export_factory,
):
    export = fba_shipment_export_factory.create() if export else None
    order = fba_shipment_order_factory.create(export=export, is_on_hold=is_on_hold)
    if shipment_package:
        fba_shipment_package_factory.create(shipment_order=order)
    assert order.is_shippable is expected


@pytest.mark.django_db
def test_close_shipment_order_method(fba_shipment_order_factory):
    shipment_order = fba_shipment_order_factory.create(export=None)
    export = shipment_order.close_shipment_order()
    shipment_order.refresh_from_db()
    assert isinstance(export, models.FBAShipmentExport)
    assert shipment_order.export == export


# Test Manager


@pytest.mark.django_db
def test_weight_kg_annotation(
    shipment_order, fba_shipment_item_factory, fba_shipment_package_factory
):
    packages = fba_shipment_package_factory.create_batch(
        3, shipment_order=shipment_order
    )
    fba_shipment_item_factory.create(package=packages[0], weight_kg=5, quantity=3)
    fba_shipment_item_factory.create(package=packages[0], weight_kg=23, quantity=2)
    fba_shipment_item_factory.create(package=packages[1], weight_kg=42, quantity=1)
    fba_shipment_item_factory.create(package=packages[1], weight_kg=32, quantity=4)
    assert models.FBAShipmentOrder.objects.get(pk=shipment_order.pk).weight_kg == 231


@pytest.mark.django_db
def test_value_annotation(
    shipment_order, fba_shipment_item_factory, fba_shipment_package_factory
):
    packages = fba_shipment_package_factory.create_batch(
        3, shipment_order=shipment_order
    )
    fba_shipment_item_factory.create(package=packages[0], value=5, quantity=3)
    fba_shipment_item_factory.create(package=packages[0], value=23, quantity=2)
    fba_shipment_item_factory.create(package=packages[1], value=42, quantity=1)
    fba_shipment_item_factory.create(package=packages[1], value=32, quantity=4)
    assert models.FBAShipmentOrder.objects.get(pk=shipment_order.pk).value == 231


@pytest.mark.django_db
def test_item_count_annotation(
    shipment_order, fba_shipment_item_factory, fba_shipment_package_factory
):
    packages = fba_shipment_package_factory.create_batch(
        3, shipment_order=shipment_order
    )
    fba_shipment_item_factory.create(package=packages[0], quantity=3)
    fba_shipment_item_factory.create(package=packages[0], quantity=2)
    fba_shipment_item_factory.create(package=packages[1], quantity=1)
    fba_shipment_item_factory.create(package=packages[1], quantity=4)
    assert models.FBAShipmentOrder.objects.get(pk=shipment_order.pk).item_count == 10
