import datetime as dt
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from imagekit.cachefiles import ImageCacheFile
from imagekit.models.fields.files import ProcessedImageFieldFile

from inventory import models
from stcadmin import settings


@pytest.fixture
def product_image(product_image_factory):
    product_image = product_image_factory.create()
    product_image.full_clean()
    return product_image


@pytest.fixture
def delete_file_exception():
    with patch(
        "django.core.files.storage.FileSystemStorage.delete",
        Mock(side_effect=Exception()),
    ) as mock_delete:
        yield mock_delete


@patch("inventory.models.product_image.settings.TESTING", False)
def test_get_storage():
    assert models.product_image.get_storage() == settings.ProductImageStorage


def test_get_storage_testing_override():
    assert models.product_image.get_storage() is None


@pytest.mark.django_db
def test_product_image_has_image_file_attribute(product_image):
    assert isinstance(product_image.image_file, ProcessedImageFieldFile)


@pytest.mark.django_db
def test_product_image_has_square_image_attribute(product_image):
    assert isinstance(product_image.square_image, ImageCacheFile)


@pytest.mark.django_db
def test_product_image_has_thumbnail_attribute(product_image):
    assert isinstance(product_image.thumbnail, ImageCacheFile)


@pytest.mark.django_db
def test_product_image_has_hash_attribute(product_image):
    assert isinstance(product_image.hash, str)
    assert len(product_image.hash) > 0


@pytest.mark.django_db
def test_product_image_has_created_at_attribute(product_image):
    assert isinstance(product_image.created_at, dt.datetime)


@pytest.mark.django_db
def test_product_image_has_modified_at_attribute(product_image):
    assert isinstance(product_image.modified_at, dt.datetime)


@pytest.mark.django_db
def test_product_image_str_method(product_image):
    assert str(product_image) == product_image.image_file.name


@pytest.mark.django_db
def test_delete_method_deletes_file(product_image):
    image_path = product_image.image_file.path
    assert Path(image_path).exists() is True
    product_image.delete()
    assert Path(image_path).exists() is False


@pytest.mark.django_db
def test_delete_method_calls_delete_thumbnail(product_image):
    image_path = Path(product_image.thumbnail.path)
    assert image_path.exists() is True
    product_image.delete()
    assert image_path.exists() is False


@pytest.mark.django_db
def test_delete_method_calls_delete_square_image(product_image):
    image_path = Path(product_image.square_image.path)
    assert image_path.exists() is True
    product_image.delete()
    assert image_path.exists() is False


@pytest.mark.django_db
def test_delete_thumbnail_method_deletes_file(product_image):
    image_path = Path(product_image.thumbnail.path)
    assert image_path.exists() is True
    product_image.delete_thumbnail()
    assert image_path.exists() is False


@pytest.mark.django_db
def test_delete_thumbnail_fails_silently_when_passed_silent_true(
    delete_file_exception, product_image
):
    product_image.delete_thumbnail(silent=True)


@pytest.mark.django_db
def test_delete_thumbnail_does_not_fail_silently_when_not_passed_silent(
    delete_file_exception, product_image
):
    with pytest.raises(Exception):
        product_image.delete_thumbnail()


@pytest.mark.django_db
def test_delete_square_image_method_deletes_file(product_image):
    image_path = Path(product_image.square_image.path)
    assert image_path.exists() is True
    product_image.delete_square_image(silent=False)
    assert image_path.exists() is False


@pytest.mark.django_db
def test_delete_square_image_fails_silently_when_passed_silent_true(
    delete_file_exception, product_image
):
    product_image.delete_square_image(silent=True)


@pytest.mark.django_db
def test_delete_square_image_does_not_fail_silently_when_not_passed_silent(
    delete_file_exception, product_image
):
    with pytest.raises(Exception):
        product_image.delete_square_image()
