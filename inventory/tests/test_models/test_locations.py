from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ValidationError

from inventory import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class CreateBays:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.warehouse_1 = models.Warehouse.objects.create(
            warehouse_ID="84616", name="Warehouse 1", abriviation="WH1"
        )
        cls.warehouse_2 = models.Warehouse.objects.create(
            warehouse_ID="94651", name="Warehouse 2", abriviation="WH2"
        )
        cls.bays = [
            models.Bay(
                bay_ID="489616",
                name="Bay 1",
                warehouse=cls.warehouse_1,
                is_default=True,
            ),
            models.Bay(
                bay_ID="156168",
                name="Bay 2",
                warehouse=cls.warehouse_1,
                is_default=False,
            ),
            models.Bay(
                bay_ID="861536",
                name="Bay 3",
                warehouse=cls.warehouse_1,
                is_default=False,
            ),
        ]
        models.Bay.objects.bulk_create(cls.bays)


class TestWarehouse(CreateBays, STCAdminTest):
    def test_str_method(self):
        self.assertEqual(str(self.warehouse_1), self.warehouse_1.name)

    @patch("inventory.models.locations.CCAPI")
    def test_get_cc_warehouses_class_method(self, mock_CCAPI):
        mock_warehouses = [Mock(id="894156")]
        mock_CCAPI.get_warehouses.return_value = mock_warehouses
        warehouses = models.Warehouse.get_cc_warehouses()
        self.assertEqual(warehouses, mock_warehouses)
        mock_CCAPI.get_warehouses.assert_called_once()

    def test_bays_property(self):
        self.assertQuerysetEqual(
            self.warehouse_1.bays,
            map(
                repr,
                models.Bay.objects.filter(warehouse=self.warehouse_1, is_default=False),
            ),
        )

    def test_default_bay_property(self):
        self.assertEqual(
            self.warehouse_1.default_bay,
            models.Bay.objects.get(warehouse=self.warehouse_1, is_default=True),
        )


class TestBays(CreateBays, STCAdminTest):
    @patch("inventory.models.locations.CCAPI")
    def test_create_bay_with_ID(self, mock_CCAPI):
        models.Bay(bay_ID="846156", warehouse=self.warehouse_1, name="New Bay").save()
        bay = models.Bay.objects.get(bay_ID="846156")
        self.assertEqual(bay.name, "New Bay")
        self.assertEqual(bay.warehouse, self.warehouse_1)
        self.assertFalse(bay.is_default)
        self.assertEqual(str(bay), "Warehouse 1 - New Bay")
        mock_CCAPI.add_bay_to_warehouse.assert_not_called()

    @patch("inventory.models.locations.CCAPI")
    def test_create_bay_without_ID(self, mock_CCAPI):
        mock_CCAPI.add_bay_to_warehouse.return_value = "846156"
        models.Bay.objects.new_bay(name="New Bay", warehouse=self.warehouse_1)
        bay = models.Bay.objects.get(bay_ID="846156")
        self.assertEqual(bay.name, "New Bay")
        self.assertEqual(bay.warehouse, self.warehouse_1)
        self.assertFalse(bay.is_default)
        self.assertEqual(str(bay), "Warehouse 1 - New Bay")
        mock_CCAPI.add_bay_to_warehouse.assert_called_once_with(
            bay="New Bay", warehouse_id=self.warehouse_1.warehouse_ID
        )

    @patch("inventory.models.locations.CCAPI")
    def test_create_backup_bay(self, mock_CCAPI):
        mock_CCAPI.add_bay_to_warehouse.return_value = "846156"
        bay = models.Bay.objects.new_backup_bay(
            name="New Bay",
            department=self.warehouse_1,
            backup_location=self.warehouse_2,
        )
        self.assertEqual(bay.name, "WH1 Backup Warehouse 2 New Bay")
        self.assertEqual(bay.warehouse, self.warehouse_1)
        self.assertFalse(bay.is_default)
        mock_CCAPI.add_bay_to_warehouse.assert_called_once_with(
            bay="WH1 Backup Warehouse 2 New Bay",
            warehouse_id=self.warehouse_1.warehouse_ID,
        )

    @patch("inventory.models.locations.CCAPI")
    def test_create_bay_with_error_getting_ID(self, mock_CCAPI):
        mock_CCAPI.add_bay_to_warehouse.return_value = None
        with self.assertRaises(Exception):
            models.Bay.objects.new_bay(name="New Bay", warehouse=self.warehouse_1)
        mock_CCAPI.add_bay_to_warehouse.assert_called_once_with(
            bay="New Bay", warehouse_id=self.warehouse_1.warehouse_ID
        )

    def test_backup_bay_name_method(self):
        self.assertEqual(
            models.Bay.objects.backup_bay_name(
                name="New Bay",
                department=self.warehouse_1,
                backup_location=self.warehouse_2,
            ),
            "WH1 Backup Warehouse 2 New Bay",
        )

    @patch("inventory.models.locations.CCAPI")
    def test_bays_with_duplicate_names_cannot_be_created(self, mock_CCAPI):
        mock_CCAPI.add_bay_to_warehouse.return_value = "846156"
        existing_bay = self.warehouse_1.bays.all()[0]
        with pytest.raises(ValidationError):
            models.Bay.objects.new_bay(
                name=existing_bay.name, warehouse=self.warehouse_1
            )
        mock_CCAPI.add_bay_to_warehouse.assert_not_called()
