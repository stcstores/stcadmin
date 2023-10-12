import pytest

from inventory.forms import AddSupplierToBlacklistForm
from inventory.models import Supplier


@pytest.fixture
def name():
    return "Blacklisted Supplier"


@pytest.fixture
def existing_supplier(name, supplier_factory):
    return supplier_factory(name=name, active=True, blacklisted=False)


@pytest.mark.django_db
def test_form_creates_blaklisted_supplier(name):
    form = AddSupplierToBlacklistForm({"name": name})
    assert form.is_valid()
    form.save()
    assert isinstance(form.instance, Supplier)
    assert form.instance.id is not None
    assert form.instance.name == name
    assert form.instance.active is True
    assert form.instance.blacklisted is True


@pytest.mark.django_db
def test_form_updates_blaklisted_supplier(name, existing_supplier):
    form = AddSupplierToBlacklistForm({"name": name})
    assert form.is_valid()
    form.save()
    assert form.instance == existing_supplier
    assert form.instance.name == name
    assert form.instance.active is True
    assert form.instance.blacklisted is True
