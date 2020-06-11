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
def test_default_vat_required(new_region):
    assert new_region.vat_required is False


@pytest.mark.django_db
def test_can_set_vat_required(name):
    region = models.Region(name=name, vat_required=True)
    region.save()
    region.refresh_from_db()
    assert region.vat_required is True


@pytest.mark.django_db
def test__str__method(region_factory, name):
    assert str(region_factory.build(name=name)) == name
