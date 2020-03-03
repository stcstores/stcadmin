import pytest
from django.db.utils import IntegrityError


@pytest.mark.django_db
def test_Category_has_name(make_category):
    category = make_category()
    assert category.name == "Test Category"


@pytest.mark.django_db
def test_Category_has_english(make_category):
    category = make_category()
    assert category.english == "Category Name"


@pytest.mark.django_db
def test_Category_has_french(make_category):
    category = make_category()
    assert category.french == "Le Typology Nom"


@pytest.mark.django_db
def test_Category_str_is_name_when_not_empty(make_category):
    category = make_category(name="Test Name")
    assert str(category) == "Test Name"


@pytest.mark.django_db
def test_Category_str_defaults_to_english_when_name_is_empty(make_category):
    category = make_category(name="", english="Sports")
    assert str(category) == "Sports"


@pytest.mark.django_db
def test_Category_name_can_be_empty(make_category):
    category = make_category(name="")
    category.save()
    assert category.name == ""


@pytest.mark.django_db
def test_Category_english_field_unique(make_category):
    english = "Test Category"
    make_category(name="One", english=english, french="Un")
    with pytest.raises(IntegrityError):
        make_category(name="Two", english=english, french="Deux")


@pytest.mark.django_db
def test_Category_french_field_unique(make_category):
    french = "Typologie"
    make_category(name="One", english="One", french=french)
    with pytest.raises(IntegrityError):
        make_category(name="One", english="Two", french=french)
