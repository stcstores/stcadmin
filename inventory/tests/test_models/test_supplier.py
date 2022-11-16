import datetime as dt

import pytest

from inventory import models


@pytest.fixture
def supplier(supplier_factory):
    supplier = supplier_factory.create()
    supplier.full_clean()
    return supplier


@pytest.fixture
def new_supplier():
    supplier = models.Supplier(name="New Supplier")
    supplier.save()
    return supplier


@pytest.mark.django_db
def test_has_name_attribute(supplier):
    assert isinstance(supplier.name, str)
    assert len(supplier.name) > 0


@pytest.mark.django_db
def test_has_active_attribute(supplier):
    assert isinstance(supplier.active, bool)


@pytest.mark.django_db
def test_active_attribute_defaults_to_true(new_supplier):
    assert new_supplier.active is True


@pytest.mark.django_db
def test_has_created_at_attribute(supplier):
    assert isinstance(supplier.created_at, dt.datetime)


@pytest.mark.django_db
def test_has_modified_at_attribute(supplier):
    assert isinstance(supplier.modified_at, dt.datetime)


@pytest.mark.django_db
def test_str_method(supplier):
    assert str(supplier) == supplier.name


@pytest.mark.django_db
def test_get_absolute_url_method(supplier):
    assert isinstance(supplier.get_absolute_url(), str)
    assert len(supplier.get_absolute_url()) > 0
