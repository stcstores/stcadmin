import pytest


@pytest.fixture
def operating_system(operating_system_factory):
    return operating_system_factory.create()


@pytest.mark.django_db
def test_full_clean(operating_system):
    assert operating_system.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_name_attribute(operating_system):
    assert isinstance(operating_system.name, str)


# Test Methods


@pytest.mark.django_db
def test_str_method(operating_system):
    assert str(operating_system) == operating_system.name
