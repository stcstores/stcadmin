import pytest

from fba import models


@pytest.fixture
def shipment_item(fba_shipment_item_factory):
    return fba_shipment_item_factory.create()


@pytest.mark.django_db
def test_full_clean(shipment_item):
    assert shipment_item.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_package_attribute(shipment_item):
    assert isinstance(shipment_item.package, models.FBAShipmentPackage)


@pytest.mark.django_db
def test_has_sku_attribute(shipment_item):
    assert isinstance(shipment_item.sku, str)


@pytest.mark.django_db
def test_has_description_attribute(shipment_item):
    assert isinstance(shipment_item.description, str)


@pytest.mark.django_db
def test_has_quantity_attribute(shipment_item):
    assert isinstance(shipment_item.quantity, int)


@pytest.mark.django_db
def test_has_weight_kg_attribute(shipment_item):
    assert isinstance(shipment_item.weight_kg, float)


@pytest.mark.django_db
def test_has_value_attribute(shipment_item):
    assert isinstance(shipment_item.value, int)


@pytest.mark.django_db
def test_has_country_of_origin_attribute(shipment_item):
    assert isinstance(shipment_item.country_of_origin, str)


@pytest.mark.django_db
def test_has_hr_code_attribute(shipment_item):
    assert isinstance(shipment_item.hr_code, str)


# Test Methods


@pytest.mark.django_db
def test_str_method(fba_shipment_item_factory):
    shipment_item = fba_shipment_item_factory.create(sku="AAA-BBB-CCC")
    shipment_item.package.pk = 5
    shipment_item.package.shipment_order.pk = 3
    assert (
        str(shipment_item)
        == "FBA Shipment Order STC_FBA_00003 package STC_FBA_00003_5 - AAA-BBB-CCC"
    )


# Test Manager


@pytest.mark.django_db
@pytest.mark.parametrize(
    "description,expected",
    (("s" * 5, "s" * 5), ("s" * 32, "s" * 32), ("s" * 33, "s" * 30 + "...")),
)
def test_short_description_annotation(description, expected, fba_shipment_item_factory):
    item = fba_shipment_item_factory.create(description=description)
    assert models.FBAShipmentItem.objects.get(pk=item.pk).short_description == expected
