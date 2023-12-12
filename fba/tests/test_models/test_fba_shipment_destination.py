import pytest

from fba import models


@pytest.fixture
def shipment_destination(fba_shipment_destination_factory):
    return fba_shipment_destination_factory.create()


@pytest.mark.django_db
def test_full_clean(shipment_destination):
    assert shipment_destination.full_clean() is None


# Test Attributes
@pytest.mark.django_db
def test_has_name_attribute(shipment_destination):
    assert isinstance(shipment_destination.name, str)


@pytest.mark.django_db
def test_has_recipient_name_attribute(shipment_destination):
    assert isinstance(shipment_destination.recipient_name, str)


@pytest.mark.django_db
def test_has_contact_telephone_attribute(shipment_destination):
    assert isinstance(shipment_destination.contact_telephone, str)


@pytest.mark.django_db
def test_has_address_line_1_attribute(shipment_destination):
    assert isinstance(shipment_destination.address_line_1, str)


@pytest.mark.django_db
def test_has_address_line_2_attribute(shipment_destination):
    assert isinstance(shipment_destination.address_line_2, str)


@pytest.mark.django_db
def test_has_address_line_3_attribute(shipment_destination):
    assert isinstance(shipment_destination.address_line_3, str)


@pytest.mark.django_db
def test_has_city_attribute(shipment_destination):
    assert isinstance(shipment_destination.city, str)


@pytest.mark.django_db
def test_has_state_attribute(shipment_destination):
    assert isinstance(shipment_destination.state, str)


@pytest.mark.django_db
def test_has_country_attribute(shipment_destination):
    assert isinstance(shipment_destination.country, str)


@pytest.mark.django_db
def test_has_country_iso_attribute(shipment_destination):
    assert isinstance(shipment_destination.country_iso, str)


@pytest.mark.django_db
def test_has_postcode_attribute(shipment_destination):
    assert isinstance(shipment_destination.postcode, str)


@pytest.mark.django_db
def test_has_is_enabled_attribute(shipment_destination):
    assert isinstance(shipment_destination.is_enabled, bool)


# Test Manager


@pytest.mark.django_db
def test_active_manager(fba_shipment_destination_factory):
    active_destination = fba_shipment_destination_factory(is_enabled=True)
    inactive_destination = fba_shipment_destination_factory(is_enabled=False)
    qs = models.FBAShipmentDestination.active.all()
    assert qs.contains(active_destination)
    assert not qs.contains(inactive_destination)


# Test Methods


@pytest.mark.django_db
def test_repr_method(fba_shipment_destination_factory):
    destination = fba_shipment_destination_factory.create(name="Some Place")
    assert repr(destination) == "<FBAShipmentDestination: Some Place>"


@pytest.mark.django_db
def test_str_method(fba_shipment_destination_factory):
    destination = fba_shipment_destination_factory.create(name="Some Place")
    assert str(destination) == "Some Place"
