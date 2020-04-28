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


@patch("fnac.tasks.models.OfferUpdate")
@pytest.mark.django_db
def test_create_offer_update_export_task(MockOfferUpdate, celery_app, celery_worker):
    tasks.create_offer_update_export.delay().get(timeout=10)
    MockOfferUpdate.objects.create_export.assert_called_once()


@patch("fnac.tasks.models.NewProductExport")
@pytest.mark.django_db
def test_create_new_product_export_task(
    MockNewProductExport, celery_app, celery_worker
):
    tasks.create_new_product_export.delay().get(timeout=10)
    MockNewProductExport.objects.create_export.assert_called_once()


@patch("fnac.tasks.models.MissingInformationImport")
@pytest.mark.django_db
def test_start_missing_information_import_task(
    MockMissingInformationImport, celery_app, celery_worker
):
    import_id = 5
    tasks.start_missing_information_import.delay(import_id).get(timeout=10)
    MockMissingInformationImport.objects.update_products.assert_called_once_with(
        import_id
    )
