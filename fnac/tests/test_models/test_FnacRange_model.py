import pytest
from django.db.utils import IntegrityError


@pytest.mark.django_db
def test_FnacRange_has_name(fnac_range_factory):
    name = "Test Name"
    fnac_range = fnac_range_factory.create(name=name)
    assert fnac_range.name == name


@pytest.mark.django_db
def test_FnacRange_has_sku(fnac_range_factory):
    sku = "RNG_ABC-DEF-123"
    fnac_range = fnac_range_factory.create(sku=sku)
    assert fnac_range.sku == sku


@pytest.mark.django_db
def test_FnacRange_has_category(fnac_range_factory, category_factory):
    category = category_factory.create()
    fnac_range = fnac_range_factory.create(category=category)
    assert fnac_range.category == category


@pytest.mark.django_db
def test_FnacRange_name_field_is_not_unique(fnac_range_factory):
    name = "Test Name"
    fnac_range_factory.create(sku="RNG_ZXV-898-POP", name=name)
    fnac_range_factory.create(sku="RNG_HGN-832-YUN", name=name)


@pytest.mark.django_db
def test_FnacRange_sku_field_is_unique(fnac_range_factory):
    sku = "RNG_ABC-DEF-123"
    fnac_range_factory.create(sku=sku)
    with pytest.raises(IntegrityError):
        fnac_range_factory.create(sku=sku)


@pytest.mark.django_db
def test_FnacRange_str(fnac_range_factory):
    fnac_range = fnac_range_factory.create(sku="RNG_ABC-DEF-123", name="Test Name")
    assert str(fnac_range) == "RNG_ABC-DEF-123 - Test Name"


@pytest.mark.django_db
def test_FnacRange_category_can_be_null(fnac_range_factory):
    fnac_range = fnac_range_factory.create(category=None)
    assert fnac_range.category is None
