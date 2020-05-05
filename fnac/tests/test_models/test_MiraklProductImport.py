import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from django.test import override_settings
from django.utils import timezone

from fnac import models


@pytest.fixture(scope="module")
def product_export_path():
    return Path(__file__).parent / "mirakl_product_export.xlsx"


@pytest.fixture
def import_file(product_export_path):
    with open(product_export_path, "rb") as f:
        yield f


@pytest.fixture
def mock_now():
    with patch("fnac.models.mirakl_product_import.timezone.now") as mock_now:
        mock_now.return_value = timezone.make_aware(datetime(2020, 3, 10))
        yield mock_now


@pytest.fixture
def import_mirakl_products_error():
    with patch(
        "fnac.models.mirakl_product_import.import_mirakl_products"
    ) as mock_import_mirakl_products:
        mock_import_mirakl_products.side_effect = Exception()
        yield mock_import_mirakl_products


@pytest.fixture
def mock_import_mirakl_products():
    with patch(
        "fnac.models.mirakl_product_import.import_mirakl_products"
    ) as mock_import_mirakl_products:
        yield mock_import_mirakl_products


@pytest.fixture()
def mock_start_mirakl_product_import_task():
    with patch(
        "fnac.models.mirakl_product_import.start_mirakl_product_import"
    ) as mock_task:
        yield mock_task


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_update_products(mock_import_mirakl_products, mirakl_product_import_factory):
    import_object = mirakl_product_import_factory.create(
        status=models.MiraklProductImport.IN_PROGRESS
    )
    models.MiraklProductImport.objects.update_products(import_object.id)
    mock_import_mirakl_products.assert_called_once_with(import_object.import_file.path)
    import_object.refresh_from_db()
    assert import_object.status == import_object.COMPLETE


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_import_mirakl_products(
    mock_now, mock_start_mirakl_product_import_task, import_file
):
    import_object = models.MiraklProductImport.objects.create_import(import_file)
    assert (
        os.path.basename(import_object.import_file.file.name)
        == models.MiraklProductImport.objects.get_filename()
    )
    assert import_object.status == import_object.IN_PROGRESS
    mock_start_mirakl_product_import_task.delay.assert_called_once_with(
        import_object.id
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_import_mirakl_products_error(
    import_mirakl_products_error, import_file, mirakl_product_import_factory
):
    import_object = mirakl_product_import_factory.create(
        status=models.MiraklProductImport.IN_PROGRESS
    )
    with pytest.raises(Exception):
        models.MiraklProductImport.objects.update_products(import_object.id)
    import_object.refresh_from_db()
    assert import_object.status == import_object.ERROR


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_import_missing_information_when_one_is_in_progress(
    mirakl_product_import_factory, import_file
):
    mirakl_product_import_factory.create(status=models.MiraklProductImport.IN_PROGRESS)
    with pytest.raises(models.MiraklProductImport.AlreadyInProgress):
        models.MiraklProductImport.objects.create_import(import_file)


def test_filename(mock_now):
    assert (
        models.MiraklProductImport.objects.get_filename()
        == "fnac_mirakl_product_import_2020-03-10.xlsx"
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_is_in_progress(mirakl_product_import_factory):
    assert models.MiraklProductImport.objects.is_in_progress() is False
    mirakl_product_import_factory.create(status=models.MiraklProductImport.IN_PROGRESS)
    assert models.MiraklProductImport.objects.is_in_progress() is True
