import os
import tempfile
from datetime import datetime
from unittest.mock import patch

import pytest
from django.test import override_settings
from django.utils import timezone

from fnac import models


@pytest.fixture
def mock_now():
    with patch("fnac.models.new_product_export.timezone.now") as mock_now:
        mock_now.return_value = timezone.make_aware(datetime(2020, 3, 10))
        yield mock_now


@pytest.fixture
def create_new_product_export_error():
    with patch(
        "fnac.models.new_product_export.create_new_product_export"
    ) as mock_create_new_product_export:
        mock_create_new_product_export.side_effect = Exception()
        yield mock_create_new_product_export


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_create_new_product_export(mock_now):
    models.NewProductExport.objects.create_export()
    assert models.NewProductExport.objects.count() == 1
    export_object = models.NewProductExport.objects.get()
    assert export_object.status == export_object.COMPLETE
    assert (
        os.path.basename(export_object.export.file.name)
        == models.NewProductExport.objects.get_filename()
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_new_product_export_error(create_new_product_export_error,):
    with pytest.raises(Exception):
        models.NewProductExport.objects.create_export()
    assert models.NewProductExport.objects.count() == 1
    export_object = models.NewProductExport.objects.get()
    assert export_object.status == export_object.ERROR
    assert bool(export_object.export) is False


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_new_product_export_when_one_is_in_progress(new_product_export_factory,):
    new_product_export_factory.create(status=models.NewProductExport.IN_PROGRESS)
    with pytest.raises(models.NewProductExport.AlreadyInProgress):
        models.NewProductExport.objects.create_export()


def test_filename(mock_now):
    assert (
        models.NewProductExport.objects.get_filename()
        == "fnac_new_products_2020-03-10.xlsx"
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_is_in_progress(new_product_export_factory,):
    assert models.NewProductExport.objects.is_in_progress() is False
    new_product_export_factory.create(status=models.NewProductExport.IN_PROGRESS)
    assert models.NewProductExport.objects.is_in_progress() is True
