import pytest
from django.core.management import call_command

from fnac import models


@pytest.fixture
def add_fixture(django_db_setup, django_db_blocker):
    def _add_fixture(fixture_name):
        with django_db_blocker.unblock():
            call_command("loaddata", fixture_name)

    return _add_fixture


@pytest.fixture
def fnac_db_fixtures(add_fixture):
    add_fixture("shipping/currency")


@pytest.fixture
def make_category():
    def _category(
        name="Test Category", english="Category Name", french="Le Typology Nom"
    ):
        category = models.Category(name=name, english=english, french=french)
        category.save()
        return category

    return _category


@pytest.fixture
def make_size():
    def _size(name="Large"):
        size = models.Size(name=name)
        size.save()
        return size

    return _size


@pytest.fixture
def make_fnac_range(make_category):
    def _fnac_range(name="Test", sku="RNG_123-HBC-3D2", category=None):
        fnac_range = models.FnacRange(name=name, sku=sku, category=category)
        fnac_range.save()
        return fnac_range

    return _fnac_range
