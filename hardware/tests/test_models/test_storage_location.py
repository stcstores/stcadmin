import pytest


@pytest.fixture
def storage_location(storage_location_factory):
    return storage_location_factory.create()


@pytest.mark.django_db
def test_full_clean(storage_location):
    assert storage_location.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_name_attribute(storage_location):
    assert isinstance(storage_location.name, str)


# Test Methods


@pytest.mark.django_db
def test_str_method(storage_location):
    assert str(storage_location) == storage_location.name
