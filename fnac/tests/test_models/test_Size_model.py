import pytest
from django.db.utils import IntegrityError


@pytest.mark.django_db
def test_Size_has_name(make_size):
    size = make_size()
    assert size.name == "Large"


@pytest.mark.django_db
def test_Size_str_matches_name(make_size):
    size = make_size()
    assert str(size) == size.name


@pytest.mark.django_db
def test_Size_name_is_unique(make_size):
    name = "Test Name"
    make_size(name=name)
    with pytest.raises(IntegrityError):
        make_size(name=name)
