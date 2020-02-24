import json
from unittest.mock import Mock, patch

from inventory import models
from inventory.tests import fixtures
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


class TestUpdateStockLevelView(InventoryViewTest, ViewTests):
    fixtures = fixtures.SingleProductRangeFixture.fixtures
    URL = "/inventory/update_stock_level/"

    old_stock_level = 5
    new_stock_level = 10

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.models.products.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)
        self.product = models.Product.objects.all()[0]
        self.mock_CCAPI.get_product.return_value = Mock(
            stock_level=self.new_stock_level
        )

    def test_post_method(self):
        data = {
            "product_ID": self.product.product_ID,
            "new_stock_level": self.new_stock_level,
            "old_stock_level": self.old_stock_level,
        }
        response = self.client.post(self.get_URL(), data)
        self.mock_CCAPI.update_product_stock_level.assert_called_once_with(
            product_id=self.product.product_ID,
            new_stock_level=self.new_stock_level,
            old_stock_level=self.old_stock_level,
        )
        self.assertEqual(str(self.new_stock_level), response.content.decode("utf8"))


class TestSetImageOrderView(InventoryViewTest, ViewTests):
    fixtures = fixtures.SingleProductRangeFixture.fixtures + (
        "inventory/product_image",
    )
    URL = "/inventory/set_image_order/"

    def request_body(self):
        data = {
            "product_ID": self.images[0].product.product_ID,
            "image_order": self.image_ids,
        }
        return json.dumps(data)

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.models.product_image.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)
        self.images = models.ProductImage.objects.filter(product__id=1)
        self.image_ids = [image.image_ID for image in self.images]

    def test_post_method(self):
        response = self.client.post(
            self.URL, self.request_body(), content_type="application/json"
        )
        self.assertEqual(200, response.status_code)
        self.mock_CCAPI.set_image_order.assert_called_once_with(
            product_id=self.images[0].product.product_ID, image_ids=self.image_ids
        )
        self.assertEqual("ok", response.content.decode("utf8"))

    def test_exception(self):
        self.mock_CCAPI.set_image_order.side_effect = Exception
        response = self.client.post(
            self.URL, self.request_body(), content_type="application/json"
        )
        self.assertEqual(500, response.status_code)


class TestDeleteImage(InventoryViewTest, ViewTests):
    fixtures = fixtures.SingleProductRangeFixture.fixtures + (
        "inventory/product_image",
    )
    URL = "/inventory/delete_image/"

    def request_body(self):
        data = {"image_id": self.image.image_ID}
        return json.dumps(data)

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.api.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)
        self.image = models.ProductImage.objects.all()[0]

    def test_post_method(self):
        response = self.client.post(
            self.URL, self.request_body(), content_type="application/json"
        )
        self.mock_CCAPI.delete_image.assert_called_once_with(self.image.image_ID)
        self.assertEqual("ok", response.content.decode("utf8"))

    def test_exception(self):
        self.mock_CCAPI.delete_image.side_effect = Exception
        response = self.client.post(
            self.URL, self.request_body(), content_type="application/json"
        )
        self.assertEqual(500, response.status_code)
