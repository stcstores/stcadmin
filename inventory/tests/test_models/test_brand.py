import datetime as dt

import pytest

from inventory import models


@pytest.fixture
def brand(brand_factory):
    brand = brand_factory.create()
    brand.full_clean()
    return brand


@pytest.fixture
def new_brand():
    brand = models.Brand(name="New Brand")
    brand.save()
    return brand


@pytest.mark.django_db
def test_brand_has_name_attribute(brand):
    assert isinstance(brand.name, str)
    assert len(brand.name) > 0


@pytest.mark.django_db
def test_brand_has_active_attribute(brand):
    assert isinstance(brand.active, bool)


@pytest.mark.django_db
def test_brand_active_attribute_defaults_to_true(new_brand):
    assert new_brand.active is True


@pytest.mark.django_db
def test_brand_has_created_at_attribute(brand):
    assert isinstance(brand.created_at, dt.datetime)


@pytest.mark.django_db
def test_brand_has_modified_at_attribute(brand):
    assert isinstance(brand.modified_at, dt.datetime)


@pytest.mark.django_db
def test_brand_str_method(brand_factory):
    name = "New Brand"
    brand = brand_factory.create(name=name)
    assert str(brand) == name
