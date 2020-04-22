from unittest.mock import patch

import pytest

from fnac import tasks


@patch("fnac.tasks.models.MissingInformationExport")
def test_create_missing_information_export_task(
    mock_MissingInformation_export, celery_app, celery_worker,
):
    tasks.create_missing_information_export.delay().get(timeout=10)
    mock_MissingInformation_export.objects.create_export.assert_called_once()


@patch("fnac.tasks.models.InventoryImport")
@pytest.mark.django_db
def test_update_inventory_task(MockInventoryImport, celery_app, celery_worker):
    tasks.update_inventory.delay().get(timeout=10)
    MockInventoryImport.objects.update_inventory.assert_called_once()
