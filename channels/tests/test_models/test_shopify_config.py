import pytest


@pytest.fixture
def shopify_config(shopify_config_factory):
    return shopify_config_factory.create()


@pytest.mark.django_db
def test_full_clean(shopify_config):
    assert shopify_config.full_clean() is None


@pytest.mark.django_db
def test_has_location_id_attribute(shopify_config):
    assert isinstance(shopify_config.location_id, str)
