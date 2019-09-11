from unittest.mock import Mock, patch

from django.test import TestCase

from inventory import models


class CreateBays:
    def setUp(self):
        super().setUp()
        self.warehouse_1 = models.Warehouse.objects.create(
            warehouse_ID="84616", name="Warehouse 1", abriviation="WH1"
        )
        self.warehouse_2 = models.Warehouse.objects.create(
            warehouse_ID="94651", name="Warehouse 2", abriviation="WH2"
        )
        self.bays = [
            models.Bay(
                bay_ID="489616",
                name="Bay 1",
                warehouse=self.warehouse_1,
                is_default=True,
            ),
            models.Bay(
                bay_ID="156168",
                name="Bay 2",
                warehouse=self.warehouse_1,
                is_default=False,
            ),
            models.Bay(
                bay_ID="861536",
                name="Bay 3",
                warehouse=self.warehouse_1,
                is_default=False,
            ),
        ]
        models.Bay.objects.bulk_create(self.bays)


class TestWarehouse(CreateBays, TestCase):
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


class TestBays(CreateBays, TestCase):
    @patch("inventory.models.locations.CCAPI")
    def test_create_bay_with_ID(self, mock_CCAPI):
        models.Bay(bay_ID="846156", warehouse=self.warehouse_1, name="New Bay").save()
        bay = models.Bay.objects.get(bay_ID="846156")
        self.assertEqual(bay.name, "New Bay")
        self.assertEqual(bay.warehouse, self.warehouse_1)
        self.assertFalse(bay.is_default)
        self.assertEqual(str(bay), "Warehouse 1 - New Bay")
        mock_CCAPI.get_bay_id.assert_not_called()

    @patch("inventory.models.locations.CCAPI")
    def test_create_bay_without_ID(self, mock_CCAPI):
        mock_CCAPI.get_bay_id.return_value = "846156"
        models.Bay(warehouse=self.warehouse_1, name="New Bay").save()
        bay = models.Bay.objects.get(bay_ID="846156")
        self.assertEqual(bay.name, "New Bay")
        self.assertEqual(bay.warehouse, self.warehouse_1)
        self.assertFalse(bay.is_default)
        self.assertEqual(str(bay), "Warehouse 1 - New Bay")
        mock_CCAPI.get_bay_id.assert_called_once_with(
            "New Bay", "Warehouse 1", create=True
        )

    @patch("inventory.models.locations.CCAPI")
    def test_create_backup_bay(self, mock_CCAPI):
        mock_CCAPI.get_bay_id.return_value = "846156"
        bay = models.Bay.new_backup_bay(
            name="New Bay",
            department=self.warehouse_1,
            backup_location=self.warehouse_2,
        )
        self.assertEqual(bay.name, "WH1 Backup Warehouse 2 New Bay")
        self.assertEqual(bay.warehouse, self.warehouse_1)
        self.assertFalse(bay.is_default)
        mock_CCAPI.get_bay_id.assert_not_called()

    @patch("inventory.models.locations.CCAPI")
    def test_create_bay_with_error_getting_ID(self, mock_CCAPI):
        mock_CCAPI.get_bay_id.return_value = None
        with self.assertRaises(Exception):
            models.Bay(warehouse=self.warehouse_1, name="New Bay").save()
        mock_CCAPI.get_bay_id.assert_called_once_with(
            "New Bay", "Warehouse 1", create=True
        )

    def test_backup_bay_name_method(self):
        self.assertEqual(
            models.Bay.backup_bay_name(
                bay_name="New Bay",
                department=self.warehouse_1,
                backup_location=self.warehouse_2,
            ),
            "WH1 Backup Warehouse 2 New Bay",
        )
