import pytest

from fnac import models


@pytest.fixture
def suppliers(supplier_factory):
    return [supplier_factory.create() for _ in range(3)]


@pytest.mark.django_db
def test_can_set_ignored_suppliers(suppliers):
    models.FnacConfig.get_solo().ignored_suppliers.set(suppliers)
    assert list(models.FnacConfig.get_solo().ignored_suppliers.all()) == suppliers
