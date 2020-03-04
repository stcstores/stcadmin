import pytest
from django.db.utils import IntegrityError


@pytest.mark.django_db
def test_Translation_name_field(translation_factory):
    name = "Chien"
    translation = translation_factory.create(name=name)
    assert translation.name == name


@pytest.mark.django_db
def test_Translation_description_field(translation_factory):
    description = (
        "<ul> <li> Puzzle de sirène de 30 pièces, personnalisé avec le "
        "nom Isabelle. </li> </ul>"
    )
    translation = translation_factory.create(description=description)
    assert translation.description == description


@pytest.mark.django_db
def test_Translation_repr(translation_factory):
    translation = translation_factory.create()
    assert repr(translation) == f"<Translations for {translation.product}>"


@pytest.mark.django_db
def test_Translation_product_field_is_unique(fnac_product_factory, translation_factory):
    product = fnac_product_factory.create()
    translation_factory.create(product=product)
    with pytest.raises(IntegrityError):
        translation_factory(product=product)
