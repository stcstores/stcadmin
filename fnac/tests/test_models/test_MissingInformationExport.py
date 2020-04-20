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
    with patch("fnac.models.add_missing_information.timezone.now") as mock_now:
        mock_now.return_value = timezone.make_aware(datetime(2020, 3, 10))
        yield mock_now


@pytest.fixture
def create_add_missing_information_export_error():
    with patch(
        "fnac.models.add_missing_information.create_add_missing_information_export"
    ) as mock_create_missing_information_export:
        mock_create_missing_information_export.side_effect = Exception()
        yield mock_create_missing_information_export


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_create_missing_information_export(mock_now):
    models.MissingInformationExport.objects.create_export()
    assert models.MissingInformationExport.objects.count() == 1
    export_object = models.MissingInformationExport.objects.get()
    assert export_object.status == export_object.COMPLETE
    assert (
        os.path.basename(export_object.export.file.name)
        == models.MissingInformationExport.objects.get_filename()
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_create_missing_information_export_error(
    create_add_missing_information_export_error,
):
    with pytest.raises(Exception):
        models.MissingInformationExport.objects.create_export()
    assert models.MissingInformationExport.objects.count() == 1
    export_object = models.MissingInformationExport.objects.get()
    assert export_object.status == export_object.ERROR
    assert bool(export_object.export) is False


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_create_missing_information_export_when_one_is_in_progress(
    missing_information_export_factory,
):
    missing_information_export_factory.create(
        status=models.MissingInformationExport.IN_PROGRESS
    )
    with pytest.raises(models.MissingInformationExport.AlreadyInProgress):
        models.MissingInformationExport.objects.create_export()


def test_filename(mock_now):
    assert (
        models.MissingInformationExport.objects.get_filename()
        == "fnac_missing_information_2020-03-10.xlsx"
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_is_in_progress(missing_information_export_factory,):
    assert models.MissingInformationExport.objects.is_in_progress() is False
    missing_information_export_factory.create(
        status=models.MissingInformationExport.IN_PROGRESS
    )
    assert models.MissingInformationExport.objects.is_in_progress() is True
