import pytest


@pytest.fixture
def shipment_config(shipment_config_factory):
    return shipment_config_factory.create()


@pytest.mark.django_db
def test_full_clean(shipment_config):
    assert shipment_config.full_clean() is None


@pytest.mark.django_db
def test_has_token_attribute(shipment_config):
    assert isinstance(shipment_config.token, str)
