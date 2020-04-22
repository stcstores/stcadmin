from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from django.utils import timezone

from fnac import models


@pytest.fixture
def product_export(db, mock_now, inventory_product_export_factory):
    return inventory_product_export_factory.create(
        timestamp=mock_now.return_value,
        export_file__from_path=Path(__file__).parent / "test_inventory.xlsx",
    )


@pytest.fixture
def mock_now():
    with patch("fnac.models.add_missing_information.timezone.now") as mock_now:
        mock_now.return_value = timezone.make_aware(datetime(2020, 3, 10))
        yield mock_now


@pytest.fixture
def mock_update_inventory():
    with patch(
        "fnac.models.inventory_update.update_inventory"
    ) as mock_update_inventory:
        yield mock_update_inventory


@pytest.fixture
def update_inventory_error(mock_update_inventory):
    mock_update_inventory.side_effect = Exception()


@pytest.mark.django_db
def test_update_inventory(mock_update_inventory, product_export, mock_now):
    models.InventoryImport.objects.update_inventory()
    assert models.InventoryImport.objects.count() == 1
    inventory_import = models.InventoryImport.objects.get()
    assert inventory_import.status == inventory_import.COMPLETE
    assert inventory_import.export == product_export
    mock_update_inventory.assert_called_once()


@pytest.mark.django_db
def test_update_inventory_error(
    product_export, update_inventory_error,
):
    with pytest.raises(Exception):
        models.InventoryImport.objects.update_inventory()
    assert models.InventoryImport.objects.count() == 1
    inventory_import = models.InventoryImport.objects.get()
    assert inventory_import.status == inventory_import.ERROR
    inventory_import.export == product_export


@pytest.mark.django_db
def test_create_missing_information_export_when_one_is_in_progress(
    product_export, inventory_import_factory,
):
    inventory_import_factory.create(status=models.InventoryImport.IN_PROGRESS)
    with pytest.raises(models.InventoryImport.AlreadyInProgress):
        models.InventoryImport.objects.update_inventory()


@pytest.mark.django_db
def test_is_in_progress(inventory_import_factory, product_export):
    assert models.InventoryImport.objects.is_in_progress() is False
    inventory_import_factory.create(status=models.InventoryImport.IN_PROGRESS)
    assert models.InventoryImport.objects.is_in_progress() is True
