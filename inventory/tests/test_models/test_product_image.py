import datetime as dt
from pathlib import Path
from unittest.mock import patch

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
def test_delete(tmp_path, product_image):
    print(product_image.thumbnail.storage)
    print(tmp_path)
    print(product_image.image_file.name)
    print(Path(product_image.image_file.path).exists())
    print(Path(product_image.square_image.path).exists())
    print(Path(product_image.thumbnail.path).exists())
    assert False
