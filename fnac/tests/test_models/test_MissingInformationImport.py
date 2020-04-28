import os
import tempfile
from datetime import datetime
from io import BytesIO
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import openpyxl
import pytest
from django.test import override_settings
from django.utils import timezone

from fnac import models
from fnac.models.add_missing_information import _MissingInformationFile


@pytest.fixture
def import_file():
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = _MissingInformationFile.PRODUCTS_SHEET
    header = _MissingInformationFile.HEADER
    for column_number, column in enumerate(header, 1):
        worksheet.cell(column=column_number, row=1).value = column
    with NamedTemporaryFile() as tmp:
        workbook.save(tmp.name)
        tmp.seek(0)
        return BytesIO(tmp.read())


@pytest.fixture
def mock_now():
    with patch("fnac.models.add_missing_information.timezone.now") as mock_now:
        mock_now.return_value = timezone.make_aware(datetime(2020, 3, 10))
        yield mock_now


@pytest.fixture
def import_missing_information_error():
    with patch(
        "fnac.models.add_missing_information.import_missing_information"
    ) as mock_import_missing_information:
        mock_import_missing_information.side_effect = Exception()
        yield mock_import_missing_information


@pytest.fixture
def mock_import_missing_information():
    with patch(
        "fnac.models.add_missing_information.import_missing_information"
    ) as mock_import_missing_information:
        yield mock_import_missing_information


@pytest.fixture()
def mock_start_missing_information_import_task():
    with patch(
        "fnac.models.add_missing_information.start_missing_information_import"
    ) as mock_task:
        yield mock_task


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_update_products(
    mock_import_missing_information, missing_information_import_factory
):
    import_object = missing_information_import_factory.create(
        status=models.MissingInformationImport.IN_PROGRESS
    )
    models.MissingInformationImport.objects.update_products(import_object.id)
    mock_import_missing_information.assert_called_once_with(
        import_object.import_file.path
    )
    import_object.refresh_from_db()
    assert import_object.status == import_object.COMPLETE


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_import_missing_information(
    mock_now, mock_start_missing_information_import_task, import_file
):
    import_object = models.MissingInformationImport.objects.create_import(import_file)
    assert (
        os.path.basename(import_object.import_file.file.name)
        == models.MissingInformationImport.objects.get_filename()
    )
    assert import_object.status == import_object.IN_PROGRESS
    mock_start_missing_information_import_task.delay.assert_called_once_with(
        import_object.id
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_import_missing_information_error(
    import_missing_information_error, import_file, missing_information_import_factory
):
    import_object = missing_information_import_factory.create(
        status=models.MissingInformationImport.IN_PROGRESS
    )
    with pytest.raises(Exception):
        models.MissingInformationImport.objects.update_products(import_object.id)
    import_object.refresh_from_db()
    assert import_object.status == import_object.ERROR


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_import_missing_information_when_one_is_in_progress(
    missing_information_import_factory, import_file
):
    missing_information_import_factory.create(
        status=models.MissingInformationImport.IN_PROGRESS
    )
    with pytest.raises(models.MissingInformationImport.AlreadyInProgress):
        models.MissingInformationImport.objects.create_import(import_file)


def test_filename(mock_now):
    assert (
        models.MissingInformationImport.objects.get_filename()
        == "fnac_missing_information_import_2020-03-10.xlsx"
    )


@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
def test_is_in_progress(missing_information_import_factory):
    assert models.MissingInformationImport.objects.is_in_progress() is False
    missing_information_import_factory.create(
        status=models.MissingInformationImport.IN_PROGRESS
    )
    assert models.MissingInformationImport.objects.is_in_progress() is True
