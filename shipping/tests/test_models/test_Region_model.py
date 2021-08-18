import pytest

from shipping import models


@pytest.fixture
def name():
    return "Test Region"


@pytest.fixture
def vat_required():
    return models.Region.VAT_ALWAYS


@pytest.fixture
def new_region(name, vat_required):
    region = models.Region(name=name, vat_required=vat_required)
    region.save()
    return region


@pytest.fixture
def default_vat_rate():
    return 17.5


@pytest.mark.django_db
def test_sets_region(new_region, name):
    assert new_region.name == name


@pytest.mark.django_db
def test_sets_abriviation(new_region):
    assert new_region.abriviation is None


@pytest.mark.django_db
def test_sets_vat_required(new_region, vat_required):
    assert new_region.vat_required == vat_required


@pytest.mark.django_db
def test_default_default_vat_rate(new_region):
    assert new_region.default_vat_rate == 20


@pytest.mark.django_db
def test_can_set_vat_required(name, vat_required):
    region = models.Region(name=name, vat_required=vat_required)
    region.save()
    region.refresh_from_db()
    assert region.vat_required == vat_required


@pytest.mark.django_db
def test_can_set_default_vat_rate(name, vat_required, default_vat_rate):
    region = models.Region(
        name=name, vat_required=vat_required, default_vat_rate=default_vat_rate
    )
    region.save()
    region.refresh_from_db()
    assert region.default_vat_rate == default_vat_rate


@pytest.mark.django_db
def test__str__method(region_factory, name):
    assert str(region_factory.build(name=name)) == name
