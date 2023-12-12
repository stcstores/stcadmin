import pytest


@pytest.fixture
def shipment_method(fba_shipment_method_factory):
    return fba_shipment_method_factory.create()


@pytest.mark.django_db
def test_full_clean(shipment_method):
    assert shipment_method.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_name_attribute(shipment_method):
    assert isinstance(shipment_method.name, str)


@pytest.mark.django_db
def test_has_identifier_attribute(shipment_method):
    assert isinstance(shipment_method.identifier, str)


@pytest.mark.django_db
def test_has_priority_attribute(shipment_method):
    assert isinstance(shipment_method.priority, int)


@pytest.mark.django_db
def test_has_is_enabled_attribute(shipment_method):
    assert isinstance(shipment_method.is_enabled, bool)


# Test Methods


@pytest.mark.django_db
def test_str_method(shipment_method):
    assert str(shipment_method) == shipment_method.name
