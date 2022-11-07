import datetime as dt
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
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


def test_product_image_get_hash_method(test_image_path, test_image_hash):
    with open(test_image_path, "rb") as f:
        uploaded_file = SimpleUploadedFile(name="file_name", content=f.read())
        hash = models.ProductImage.objects.get_hash(uploaded_file)
    assert hash == test_image_hash


@pytest.fixture
def uploaded_file(test_image_path):
    with open(test_image_path, "rb") as f:
        yield SimpleUploadedFile(name="file_name", content=f.read())


@pytest.fixture
def added_image(uploaded_file):
    return models.ProductImage.objects.add_image(uploaded_file=uploaded_file)


class TestAddImageMethod:
    @pytest.mark.django_db
    def test_image_is_added(self, added_image):
        assert isinstance(added_image.id, int)

    @pytest.mark.django_db
    def test_image_has_hash(self, added_image, test_image_hash):
        assert added_image.hash == test_image_hash

    @pytest.mark.django_db
    @patch("inventory.models.product_image.ProductImageManager.get_hash")
    def test_get_hash_is_not_called_when_hash_string_is_passed(
        self, mock_get_hash, uploaded_file
    ):
        models.ProductImage.objects.add_image(
            uploaded_file=uploaded_file, hash_string="FAKEHASHSTRING"
        )
        mock_get_hash.assert_not_called()

    @pytest.mark.django_db
    def test_get_hash_string_is_used_when_passed(self, uploaded_file):
        hash_string = "FAKEHASHSTRING"
        image_object = models.ProductImage.objects.add_image(
            uploaded_file=uploaded_file, hash_string=hash_string
        )
        assert image_object.hash == hash_string


class TestGetOrAddImageMethod:
    @pytest.fixture
    def existing_image(self, test_image_hash, product_image_factory):
        return product_image_factory.create(hash=test_image_hash)

    @pytest.mark.django_db
    def test_get_or_add_image_creates_an_image_if_no_match_is_found(
        self, uploaded_file
    ):
        image = models.ProductImage.objects.get_or_add_image(
            uploaded_file=uploaded_file
        )
        assert isinstance(image.id, int)

    @pytest.mark.django_db
    def test_returns_existing_image_if_a_match_is_found(
        self, existing_image, uploaded_file
    ):
        new_image = models.ProductImage.objects.get_or_add_image(
            uploaded_file=uploaded_file
        )
        assert new_image.id == existing_image.id
        assert models.ProductImage.objects.count() == 1

    @pytest.mark.django_db
    @patch("inventory.models.product_image.ProductImageManager.add_image")
    def test_does_not_call_add_image_when_match_is_found(
        self, mock_add_image, uploaded_file, existing_image
    ):
        models.ProductImage.objects.get_or_add_image(uploaded_file=uploaded_file)
        mock_add_image.assert_not_called()

    @pytest.mark.django_db
    @patch("inventory.models.product_image.ProductImageManager.add_image")
    def test_calls_add_image_when_no_match_is_found(
        self, mock_add_image, uploaded_file, test_image_hash
    ):
        models.ProductImage.objects.get_or_add_image(uploaded_file=uploaded_file)
        mock_add_image.assert_called_once_with(
            uploaded_file=uploaded_file, hash_string=test_image_hash
        )
