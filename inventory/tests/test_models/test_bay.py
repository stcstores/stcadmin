import datetime as dt

import pytest

from inventory.models import Bay


@pytest.fixture
def bay(bay_factory):
    bay = bay_factory.create()
    bay.full_clean()
    return bay


@pytest.fixture
def new_bay():
    bay = Bay(name="test_name")
    bay.save()
    return bay


@pytest.mark.django_db
def test_bay_has_name_attribute(bay):
    assert isinstance(bay.name, str)
    assert len(bay.name) > 0


@pytest.mark.django_db
def test_bay_has_active_attribute(bay):
    assert isinstance(bay.active, bool)


@pytest.mark.django_db
def test_bay_active_attribute_defaults_to_true(new_bay):
    assert new_bay.active is True


@pytest.mark.django_db
def test_bay_has_created_at_attribute(bay):
    assert isinstance(bay.created_at, dt.datetime)


@pytest.mark.django_db
def test_bay_has_modified_at_attribute(bay):
    assert isinstance(bay.modified_at, dt.datetime)


@pytest.mark.django_db
def test_bay_str_method(bay):
    assert str(bay) == bay.name
