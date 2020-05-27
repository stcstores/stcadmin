import pytest

from shipping import models


@pytest.fixture
def name():
    return "Test Region"


@pytest.fixture
def new_region(name):
    region = models.Region(name=name)
    region.save()
    return region


@pytest.mark.django_db
def test_sets_region(new_region, name):
    assert new_region.name == name


@pytest.mark.django_db
def test_sets_abriviation(new_region):
    assert new_region.abriviation is None


@pytest.mark.django_db
def test__str__method(region_factory, name):
    assert str(region_factory.build(name=name)) == name
