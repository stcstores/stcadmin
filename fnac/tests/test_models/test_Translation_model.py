import pytest
from django.db.utils import IntegrityError


@pytest.mark.django_db
def test_Translation_name_field(make_translation):
    name = "Chien"
    translation = make_translation(name=name)
    assert translation.name == name


@pytest.mark.django_db
def test_Translation_description_field(make_translation):
    description = (
        "<ul> <li> Puzzle de sirène de 30 pièces, personnalisé avec le "
        "nom Isabelle. </li> </ul>"
    )
    translation = make_translation(description=description)
    assert translation.description == description


@pytest.mark.django_db
def test_Translation_repr(make_translation):
    translation = make_translation()
    assert repr(translation) == f"<Translations for {translation.product}>"


@pytest.mark.django_db
def test_Translation_product_field_is_unique(make_fnac_product, make_translation):
    product = make_fnac_product()
    make_translation(product=product)
    with pytest.raises(IntegrityError):
        make_translation(product=product)
