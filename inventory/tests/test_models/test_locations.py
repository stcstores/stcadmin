from unittest.mock import Mock, patch

from django.test import TestCase

from inventory import models


class TestWarehouse(TestCase):
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
