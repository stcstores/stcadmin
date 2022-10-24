import datetime as dt

import pytest

from inventory import models


@pytest.fixture
def manufacturer(manufacturer_factory):
    manufacturer = manufacturer_factory.create()
    manufacturer.full_clean()
    return manufacturer


@pytest.fixture
def new_manufacturer():
    manufacturer = models.Manufacturer(name="New Manufacturer")
    manufacturer.save()
    return manufacturer


@pytest.mark.django_db
def test_manufacturer_has_name_attribute(manufacturer):
    assert isinstance(manufacturer.name, str)
    assert len(manufacturer.name) > 0


@pytest.mark.django_db
def test_manufacturer_has_active_attribute(manufacturer):
    assert isinstance(manufacturer.active, bool)


@pytest.mark.django_db
def test_manufacturer_active_attribute_defaults_to_true(new_manufacturer):
    assert new_manufacturer.active is True


@pytest.mark.django_db
def test_manufacturer_has_created_at_attribute(manufacturer):
    assert isinstance(manufacturer.created_at, dt.datetime)


@pytest.mark.django_db
def test_manufacturer_has_modified_at_attribute(manufacturer):
    assert isinstance(manufacturer.modified_at, dt.datetime)


@pytest.mark.django_db
def test_manufacturer_str_method(manufacturer_factory):
    name = "New Manufacturer"
    manufacturer = manufacturer_factory.create(name=name)
    assert str(manufacturer) == name
