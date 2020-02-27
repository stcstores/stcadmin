import pytest
from django.db.utils import IntegrityError


@pytest.mark.django_db
def test_FnacRange_has_name(make_fnac_range):
    name = "Test Name"
    fnac_range = make_fnac_range(name=name)
    assert fnac_range.name == name


@pytest.mark.django_db
def test_FnacRange_has_sku(make_fnac_range):
    sku = "RNG_ABC-DEF-123"
    fnac_range = make_fnac_range(sku=sku)
    assert fnac_range.sku == sku


@pytest.mark.django_db
def test_FnacRange_has_category(make_fnac_range, make_category):
    category = make_category()
    fnac_range = make_fnac_range(category=category)
    assert fnac_range.category == category


@pytest.mark.django_db
def test_FnacRange_name_field_is_unique(make_fnac_range):
    name = "Test Name"
    make_fnac_range(name=name)
    with pytest.raises(IntegrityError):
        make_fnac_range(name=name)


@pytest.mark.django_db
def test_FnacRange_sku_field_is_unique(make_fnac_range):
    sku = "RNG_ABC-DEF-123"
    make_fnac_range(sku=sku)
    with pytest.raises(IntegrityError):
        make_fnac_range(sku=sku)


@pytest.mark.django_db
def test_FnacRange_str(make_fnac_range):
    fnac_range = make_fnac_range(sku="RNG_ABC-DEF-123", name="Test Name")
    assert str(fnac_range) == "RNG_ABC-DEF-123 - Test Name"


@pytest.mark.django_db
def test_FnacRange_category_can_be_null(make_fnac_range):
    fnac_range = make_fnac_range(category=None)
    assert fnac_range.category is None
