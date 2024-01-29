import pytest


@pytest.fixture
def hardware_use(hardware_use_factory):
    return hardware_use_factory.create()


@pytest.mark.django_db
def test_full_clean(hardware_use):
    assert hardware_use.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_name_attribute(hardware_use):
    assert isinstance(hardware_use.name, str)


@pytest.mark.django_db
def test_has_location_attribute(hardware_use):
    assert isinstance(hardware_use.location, str)


@pytest.mark.django_db
def test_has_primary_user_attribute(hardware_use):
    assert isinstance(hardware_use.primary_user, str)


@pytest.mark.django_db
def test_has_primary_use_attribute(hardware_use):
    assert isinstance(hardware_use.primary_use, str)


# Test Methods


@pytest.mark.django_db
def test_str_method(hardware_use):
    assert str(hardware_use) == hardware_use.name
