import pytest
from django.db.utils import IntegrityError


@pytest.mark.django_db
def test_Category_has_name(category_factory):
    name = "Test Category"
    category = category_factory.create(name=name)
    assert category.name == name


@pytest.mark.django_db
def test_Category_has_english(category_factory):
    english = "Category Name"
    category = category_factory.create(english=english)
    assert category.english == english


@pytest.mark.django_db
def test_Category_has_french(category_factory):
    french = "Le Typology Nom"
    category = category_factory.create(french=french)
    assert category.french == french


@pytest.mark.django_db
def test_Category_has_requires_colour(category_factory):
    category = category_factory.create(requires_colour=True)
    assert category.requires_colour is True


@pytest.mark.django_db
def test_Category_str_is_name_when_not_empty(category_factory):
    category = category_factory.create(name="Test Name")
    assert str(category) == "Test Name"


@pytest.mark.django_db
def test_Category_str_defaults_to_english_when_name_is_empty(category_factory):
    category = category_factory.create(name="", english="Sports")
    assert str(category) == "Sports"


@pytest.mark.django_db
def test_Category_name_can_be_empty(category_factory):
    category = category_factory.create(name="")
    category.save()
    assert category.name == ""


@pytest.mark.django_db
def test_Category_english_field_unique(category_factory):
    english = "Test Category"
    category_factory.create(english=english)
    with pytest.raises(IntegrityError):
        category_factory.create(english=english)


@pytest.mark.django_db
def test_Category_french_field_unique(category_factory):
    french = "Typologie"
    category_factory.create(french=french)
    with pytest.raises(IntegrityError):
        category_factory.create(french=french)
