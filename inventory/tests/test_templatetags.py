import json
from unittest.mock import patch

from inventory import models
from inventory.templatetags import inventory_extras
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestCCPProductRangePage(STCAdminTest):
    @patch("inventory.templatetags.inventory_extras.URLs")
    def test_ccp_product_range_page(self, mock_URLs):
        range_ID = "384937"
        return_value = inventory_extras.SUBDOMAIN + range_ID
        mock_URLs.range_url.return_value = return_value
        result = inventory_extras.ccp_product_range_page(range_ID)
        mock_URLs.range_url.assert_called_once_with(
            inventory_extras.SUBDOMAIN, range_ID
        )
        self.assertEqual(return_value, result)


class TestCCPProductPage(STCAdminTest):
    @patch("inventory.templatetags.inventory_extras.URLs")
    def test_ccp_product_page(self, mock_URLs):
        range_ID = "384937"
        product_ID = "28404839"
        return_value = inventory_extras.SUBDOMAIN + range_ID + product_ID
        mock_URLs.product_url.return_value = return_value
        result = inventory_extras.ccp_product_page(range_ID, product_ID)
        mock_URLs.product_url.assert_called_once_with(
            inventory_extras.SUBDOMAIN, range_ID, product_ID
        )
        self.assertEqual(return_value, result)


class TestWarehouses(STCAdminTest):
    @classmethod
    def setUpTestData(cls):
        cls.warehouse_1 = models.Warehouse.objects.create(
            name="Warehouse 1", abriviation="WH1", warehouse_ID="284939"
        )
        cls.warehouse_2 = models.Warehouse.objects.create(
            name="Warehouse 2", abriviation="WH2", warehouse_ID="846146"
        )
        cls.bay_1 = models.Bay.objects.create(
            name="Bay 1", bay_ID="2849302", warehouse=cls.warehouse_1
        )
        cls.bay_2 = models.Bay.objects.create(
            name="Bay 2", bay_ID="5161516", warehouse=cls.warehouse_1
        )
        cls.bay_3 = models.Bay.objects.create(
            name="Bay 3", bay_ID="8131997", warehouse=cls.warehouse_1
        )
        cls.bay_4 = models.Bay.objects.create(
            name="Bay 4", bay_ID="9411356", warehouse=cls.warehouse_2
        )
        cls.bay_5 = models.Bay.objects.create(
            name="Bay 5", bay_ID="9431155", warehouse=cls.warehouse_2
        )

    def test_warehouses(self):
        self.assertEqual(
            json.dumps(
                {
                    self.warehouse_1.id: [
                        {"value": bay.id, "text": bay.name}
                        for bay in (self.bay_1, self.bay_2, self.bay_3)
                    ],
                    self.warehouse_2.id: [
                        {"value": bay.id, "text": bay.name}
                        for bay in (self.bay_4, self.bay_5)
                    ],
                }
            ),
            inventory_extras.warehouses(),
        )

    def test_warehouses_with_no_warehouses(self):
        models.Warehouse.objects.all().delete()
        self.assertEqual("{}", inventory_extras.warehouses())
