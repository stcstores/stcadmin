import json
from unittest.mock import patch

from inventory.tests import mocks
from stcadmin.tests.stcadmin_test import ViewTests

from .test_views import InventoryViewTest


class TestGetNewSKUView(InventoryViewTest, ViewTests):
    URL = "/inventory/get_new_sku/"

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.api.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

    def test_post_method(self):
        sku = "ABC-DEF-123"
        self.mock_CCAPI.get_sku.return_value = sku
        response = self.client.post(self.get_URL())
        self.mock_CCAPI.get_sku.assert_called_once_with(range_sku=False)
        self.assertEqual(sku, response.content.decode("utf8"))


class TestGetNewRangeSKUView(InventoryViewTest, ViewTests):
    URL = "/inventory/get_new_range_sku/"

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.api.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

    def test_post_method(self):
        sku = "RNG_ABC-DEF-123"
        self.mock_CCAPI.get_sku.return_value = sku
        response = self.client.post(self.get_URL())
        self.mock_CCAPI.get_sku.assert_called_once_with(range_sku=True)
        self.assertEqual(sku, response.content.decode("utf8"))


class TestGetStockForProductView(InventoryViewTest, ViewTests):
    URL = "/inventory/get_stock_for_products/"

    product_id = "28493839"

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.api.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)
        self.product = mocks.MockCCAPIProduct(id=self.product_id)
        self.mock_CCAPI.get_product.return_value = self.product

    def test_post_method(self):
        body = json.dumps({"variation_ids": [self.product_id]})
        response = self.client.post(
            self.get_URL(), body, content_type="application/json"
        )
        self.mock_CCAPI.get_product.assert_called_once_with(self.product_id)
        expected_response = [
            {
                "variation_id": self.product.id,
                "stock_level": self.product.stock_level,
                "locations": self.product.locations[0].name,
            }
        ]
        self.assertEqual(json.dumps(expected_response), response.content.decode("utf8"))


class TestUpdateStockLevelView(InventoryViewTest, ViewTests):
    URL = "/inventory/update_stock_level/"

    product_id = "28493839"
    sku = "ABC-DEF-123"
    old_stock_level = 5
    new_stock_level = 10

    def set_stock_level(self):
        self.product.stock_level = self.new_stock_level

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.api.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)
        self.product = mocks.MockCCAPIProduct(id=self.product_id)
        self.mock_CCAPI.get_product.return_value = self.product
        self.mock_CCAPI.update_product_stock_level.side_effect = self.set_stock_level()

    def test_post_method(self):
        data = {
            "product_id": self.product_id,
            "sku": self.sku,
            "new_stock_level": self.new_stock_level,
            "old_stock_level": self.old_stock_level,
        }
        body = json.dumps(data)
        response = self.client.post(
            self.get_URL(), body, content_type="application/json"
        )
        self.mock_CCAPI.get_product.assert_called_once_with(self.product_id)
        self.mock_CCAPI.update_product_stock_level.assert_called_once_with(
            product_id=self.product_id,
            new_stock_level=self.new_stock_level,
            old_stock_level=self.old_stock_level,
        )
        self.assertEqual(str(self.new_stock_level), response.content.decode("utf8"))
        self.assertEqual(self.new_stock_level, self.product.stock_level)


class TestSetImageOrderView(InventoryViewTest, ViewTests):
    URL = "/inventory/set_image_order/"

    product_id = "28493839"
    image_ids = ["945156468", "66161561", "89748161", "86161681"]

    def request_body(self):
        data = {"product_id": self.product_id, "image_order": self.image_ids}
        return json.dumps(data)

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.api.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

    def test_post_method(self):
        response = self.client.post(
            self.URL, self.request_body(), content_type="application/json"
        )
        self.mock_CCAPI.set_image_order.assert_called_once_with(
            product_id=self.product_id, image_ids=self.image_ids
        )
        self.assertEqual("ok", response.content.decode("utf8"))

    def test_exception(self):
        self.mock_CCAPI.set_image_order.side_effect = Exception
        response = self.client.post(
            self.URL, self.request_body(), content_type="application/json"
        )
        self.assertEqual(500, response.status_code)


class TestDeleteImage(InventoryViewTest, ViewTests):
    URL = "/inventory/delete_image/"

    image_id = "945156468"

    def request_body(self):
        data = {"image_id": self.image_id}
        return json.dumps(data)

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.api.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

    def test_post_method(self):
        response = self.client.post(
            self.URL, self.request_body(), content_type="application/json"
        )
        self.mock_CCAPI.delete_image.assert_called_once_with(self.image_id)
        self.assertEqual("ok", response.content.decode("utf8"))

    def test_exception(self):
        self.mock_CCAPI.delete_image.side_effect = Exception
        response = self.client.post(
            self.URL, self.request_body(), content_type="application/json"
        )
        self.assertEqual(500, response.status_code)
