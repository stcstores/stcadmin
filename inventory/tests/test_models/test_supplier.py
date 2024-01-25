import datetime as dt

import pytest

from inventory import models


@pytest.fixture
def supplier(supplier_factory):
    supplier = supplier_factory.create()
    supplier.full_clean()
    return supplier


@pytest.fixture
def inactive_supplier(supplier_factory):
    return supplier_factory.create(active=False)


@pytest.fixture
def blacklisted_supplier(supplier_factory):
    return supplier_factory.create(blacklisted=True)


@pytest.fixture
def inactive_blacklisted_supplier(supplier_factory):
    return supplier_factory.create(active=False, blacklisted=True)


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
def test_has_last_ordered_from_attribute(supplier):
    assert isinstance(supplier.last_ordered_from, dt.date)


@pytest.mark.django_db
def test_last_ordered_from_attribute_defaults_to_none(new_supplier):
    assert new_supplier.last_ordered_from is None


@pytest.mark.django_db
def test_has_restock_comment(supplier):
    assert isinstance(supplier.restock_comment, str)


@pytest.mark.django_db
def test_restock_comment_defaults_to_empty_string(new_supplier):
    assert new_supplier.restock_comment == ""


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


@pytest.mark.django_db
def test_active_filter(
    supplier, inactive_supplier, blacklisted_supplier, inactive_blacklisted_supplier
):
    qs = models.Supplier.objects.active()
    assert qs.contains(supplier)
    assert not qs.contains(inactive_supplier)
    assert not qs.contains(blacklisted_supplier)
    assert not qs.contains(inactive_blacklisted_supplier)


@pytest.mark.django_db
def test_inactive_filter(
    supplier, inactive_supplier, blacklisted_supplier, inactive_blacklisted_supplier
):
    qs = models.Supplier.objects.inactive()
    assert not qs.contains(supplier)
    assert qs.contains(inactive_supplier)
    assert not qs.contains(blacklisted_supplier)
    assert not qs.contains(inactive_blacklisted_supplier)


@pytest.mark.django_db
def test_blacklisted_filter(
    supplier, inactive_supplier, blacklisted_supplier, inactive_blacklisted_supplier
):
    qs = models.Supplier.objects.blacklisted()
    assert not qs.contains(supplier)
    assert not qs.contains(inactive_supplier)
    assert qs.contains(blacklisted_supplier)
    assert qs.contains(inactive_blacklisted_supplier)
