import pytest
from django.db.utils import IntegrityError


@pytest.mark.django_db
def test_Size_has_name(size_factory):
    name = "Large"
    size = size_factory.create(name=name)
    assert size.name == name


@pytest.mark.django_db
def test_Size_str_matches_name(size_factory):
    size = size_factory.create()
    assert str(size) == size.name


@pytest.mark.django_db
def test_Size_name_is_unique(size_factory):
    name = "Test Name"
    size_factory.create(name=name)
    with pytest.raises(IntegrityError):
        size_factory.create(name=name)
