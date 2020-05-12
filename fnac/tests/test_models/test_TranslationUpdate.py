from datetime import datetime
from unittest.mock import patch

import pytest
from django.utils import timezone

from fnac import models
from fnac.models.translation import update_translations


@pytest.fixture
def products(fnac_product_factory):
    return [
        fnac_product_factory.create(sku="5AM-8UM-7AN"),
        fnac_product_factory.create(sku="4AM-A1M-R2P"),
    ]


@pytest.fixture
def names():
    return ["Produit un titre", "Titre du produit deux"]


@pytest.fixture
def descriptions():
    return [
        "<p> Une description d'un produit </p>\r\n<p> Il est rouge </p>",
        "Une description d'un produit\r\nIl n'a pas de couleur",
    ]


@pytest.fixture
def colours():
    return ["rouge", ""]


@pytest.fixture
def translation_import_text():
    return "\r\n".join(
        [
            "SKU \tTitre \tCouleur \tLa description \t¬",
            "5 AM-8UM-7AN \tProduit un titre \trouge \t<p> Une description d'un produit </p>\r\n<p> Il est rouge </p> \t¬",
            "4 AM-A1M-R2P \tTitre du produit deux \tAucun \tUne description d'un produit\r\nIl n'a pas de couleur \t¬",
        ]
    )


@pytest.fixture
def translation_import(products, translation_import_text, translation_update_factory):
    update_translations(translation_import_text)


@pytest.fixture
def mock_now():
    with patch("fnac.models.add_missing_information.timezone.now") as mock_now:
        mock_now.return_value = timezone.make_aware(datetime(2020, 3, 10))
        yield mock_now


@pytest.fixture
def mock_update_translations_error():
    with patch(
        "fnac.models.translation.update_translations"
    ) as mock_update_translations:
        mock_update_translations.side_effect = Exception()
        yield mock_update_translations


@pytest.fixture
def mock_translation_update():
    with patch(
        "fnac.models.translation.update_translations"
    ) as mock_update_translations:
        yield mock_update_translations


@pytest.fixture()
def mock_start_translation_update_task():
    with patch("fnac.models.translation.start_translation_update") as mock_task:
        yield mock_task


@pytest.mark.django_db
def test_translation_created(products, translation_import):
    for product in products:
        product.refresh_from_db()
        assert product.translation is not None


@pytest.mark.django_db
def test_translation_names(products, names, translation_import):
    for product, name in zip(products, names):
        product.refresh_from_db()
        assert product.translation.name == name


@pytest.mark.django_db
def test_translation_descriptions(products, descriptions, translation_import):
    for product, description in zip(products, descriptions):
        product.refresh_from_db()
        assert product.translation.description == description


@pytest.mark.django_db
def test_translation_colours(products, colours, translation_import):
    for product, colour in zip(products, colours):
        product.refresh_from_db()
        assert product.translation.colour == colour


@pytest.mark.django_db
def test_existing_translations_are_updated(translation_factory, translation_import):
    translation = translation_factory.create()
    product = translation.product
    translation_text = "\r\n".join(
        [
            "SKU \tTitre \tCouleur \tLa description \t¬",
            f"{product.sku} \tProduit un titre \trouge \tUne description d'un produit\t¬",
        ]
    )
    update_translations(translation_text)
    translation.refresh_from_db()
    assert translation.product == product
    assert translation.name == "Produit un titre"
    assert translation.colour == "rouge"
    assert translation.description == "Une description d'un produit"


@pytest.mark.django_db
def test_update_translations(mock_translation_update, translation_update_factory):
    update_object = translation_update_factory.create(
        status=models.TranslationUpdate.IN_PROGRESS
    )
    models.TranslationUpdate.objects.update_translations(update_object.id)
    mock_translation_update.assert_called_once_with(update_object.translation_text)
    update_object.refresh_from_db()
    assert update_object.status == update_object.COMPLETE


@pytest.mark.django_db
def test_create_update(
    mock_now, mock_start_translation_update_task, translation_import_text
):
    update_object = models.TranslationUpdate.objects.create_update(
        translation_import_text
    )
    assert update_object.status == update_object.IN_PROGRESS
    mock_start_translation_update_task.delay.assert_called_once_with(update_object.id)


@pytest.mark.django_db
def test_update_translations_error(
    mock_update_translations_error, translation_update_factory
):
    update_object = translation_update_factory.create(
        status=models.TranslationUpdate.IN_PROGRESS
    )
    with pytest.raises(Exception):
        models.TranslationUpdate.objects.update_translations(update_object.id)
    update_object.refresh_from_db()
    assert update_object.status == update_object.ERROR


@pytest.mark.django_db
def test_import_missing_information_when_one_is_in_progress(
    translation_update_factory, translation_import_text
):
    translation_update_factory.create(status=models.TranslationUpdate.IN_PROGRESS)
    with pytest.raises(models.TranslationUpdate.AlreadyInProgress):
        models.TranslationUpdate.objects.create_update(translation_import_text)


@pytest.mark.django_db
def test_is_in_progress(translation_update_factory):
    assert models.TranslationUpdate.objects.is_in_progress() is False
    translation_update_factory.create(status=models.TranslationUpdate.IN_PROGRESS)
    assert models.TranslationUpdate.objects.is_in_progress() is True
