import json
from unittest.mock import Mock, patch

from django.shortcuts import reverse

from inventory import models
from inventory.tests.test_models.test_products import SetupSingleProductRange

from .inventory_view_test import InventoryViewTest


class TestGetNewSKUView(InventoryViewTest):
    @patch("inventory.views.api.CCAPI.get_sku")
    def test_get_method(self, mock_get_sku):
        self.supplier = models.Supplier.objects.create(
            name="Stock Inc", product_option_value_ID="165415", factory_ID="84135"
        )
        sku = b"JSL-8DX-J5T"
        mock_get_sku.return_value = sku
        response = self.client.get(reverse("inventory:get_new_sku"))
        mock_get_sku.assert_called_once_with(range_sku=False)
        self.assertEqual(response.content, sku)


class TestGetNewRangeSKUView(InventoryViewTest):
    @patch("inventory.views.api.CCAPI.get_sku")
    def test_get_method(self, mock_get_sku):
        self.supplier = models.Supplier.objects.create(
            name="Stock Inc", product_option_value_ID="165415", factory_ID="84135"
        )
        sku = b"RNG_JSL-8DX-J5T"
        mock_get_sku.return_value = sku
        response = self.client.get(reverse("inventory:get_new_range_sku"))
        mock_get_sku.assert_called_once_with(range_sku=True)
        self.assertEqual(response.content, sku)


class TestUpdateStockLevelView(SetupSingleProductRange, InventoryViewTest):
    @patch("inventory.models.products.CCAPI")
    def test_post_method(self, mock_CCAPI):
        old_stock_level = 1
        new_stock_level = 6
        updated_stock_level = 5
        mock_CCAPI.get_product.return_value = Mock(stock_level=updated_stock_level)
        response = self.client.post(
            reverse("inventory:update_stock_level"),
            {
                "product_ID": self.product.product_ID,
                "new_stock_level": new_stock_level,
                "old_stock_level": old_stock_level,
            },
        )
        self.assertEqual(response.content, b"5")
        mock_CCAPI.get_product.assert_called_once_with(self.product.product_ID)
        mock_CCAPI.update_product_stock_level.assert_called_once_with(
            product_id=self.product.product_ID,
            old_stock_level=old_stock_level,
            new_stock_level=new_stock_level,
        )


class TestGetStockLevelView(SetupSingleProductRange, InventoryViewTest):
    @patch("inventory.models.products.CCAPI")
    def test_post_method(self, mock_CCAPI):
        mock_CCAPI.get_product.return_value = Mock(stock_level=5)
        response = self.client.post(
            reverse("inventory:get_stock_level"),
            {"product_ID": self.product.product_ID},
        )
        expected_response = json.dumps(
            {"product_ID": self.product.product_ID, "stock_level": 5}
        ).encode("utf8")
        self.assertEqual(response.content, expected_response)
        mock_CCAPI.get_product.assert_called_once_with(self.product.product_ID)
