import json
from unittest.mock import Mock, patch

from django.shortcuts import reverse

from inventory import models
from inventory.tests import fixtures
from stcadmin.tests.stcadmin_test import ViewTests

from .inventory_view_test import InventoryViewTest


class APIViewTests(ViewTests):
    @patch("inventory.views.api.CCAPI")
    def test_get_method(self, mock_CCAPI):
        super().test_get_method()
        self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.views.api.CCAPI")
    def test_logged_out_user_get(self, mock_CCAPI):
        super().test_logged_out_user_get()
        self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.views.api.CCAPI")
    def test_logged_out_user_post(self, mock_CCAPI):
        super().test_logged_out_user_post()
        self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.views.api.CCAPI")
    def test_user_not_in_group_get(self, mock_CCAPI):
        super().test_user_not_in_group_get()
        self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.views.api.CCAPI")
    def test_user_not_in_group_post(self, mock_CCAPI):
        super().test_user_not_in_group_get()
        self.assertEqual(0, len(mock_CCAPI.mock_calls))


class TestGetNewSKUView(InventoryViewTest, APIViewTests):
    URL = "/inventory/get_new_sku/"

    @patch("inventory.views.api.CCAPI")
    def test_post_method(self, mock_CCAPI):
        self.supplier = models.Supplier.objects.create(
            name="Stock Inc", product_option_value_ID="165415", factory_ID="84135"
        )
        sku = "JSL-8DX-J5T"
        mock_CCAPI.get_sku.return_value = sku
        response = self.client.post(self.URL)
        mock_CCAPI.get_sku.assert_called_once_with(range_sku=False)
        self.assertEqual(1, len(mock_CCAPI.mock_calls))
        self.assertEqual(sku, response.content.decode("utf8"))


class TestGetNewRangeSKUView(InventoryViewTest, APIViewTests):
    URL = "/inventory/get_new_range_sku/"

    @patch("inventory.views.api.CCAPI")
    def test_post_method(self, mock_CCAPI):
        self.supplier = models.Supplier.objects.create(
            name="Stock Inc", product_option_value_ID="165415", factory_ID="84135"
        )
        sku = "RNG_JSL-8DX-J5T"
        mock_CCAPI.get_sku.return_value = sku
        response = self.client.post(self.URL)
        mock_CCAPI.get_sku.assert_called_once_with(range_sku=True)
        self.assertEqual(1, len(mock_CCAPI.mock_calls))
        self.assertEqual(sku, response.content.decode("utf8"))


class TestUpdateStockLevelView(
    InventoryViewTest, APIViewTests, fixtures.SingleProductRangeFixture
):
    fixtures = fixtures.SingleProductRangeFixture.fixtures

    URL = "/inventory/update_stock_level/"

    @patch("inventory.models.products.CCAPI")
    def test_post_method(self, mock_CCAPI):
        old_stock_level = 1
        new_stock_level = 6
        updated_stock_level = 5
        mock_CCAPI.get_product.return_value = Mock(stock_level=updated_stock_level)
        form_data = {
            "product_ID": self.product.product_ID,
            "new_stock_level": new_stock_level,
            "old_stock_level": old_stock_level,
        }
        response = self.client.post(self.URL, form_data)
        self.assertEqual(b"5", response.content)
        mock_CCAPI.get_product.assert_called_once_with(self.product.product_ID)
        mock_CCAPI.update_product_stock_level.assert_called_once_with(
            product_id=self.product.product_ID,
            old_stock_level=old_stock_level,
            new_stock_level=new_stock_level,
        )
        self.assertEqual(2, len(mock_CCAPI.mock_calls))

    @patch("inventory.models.products.CCAPI")
    def test_invalid_product_ID(self, mock_CCAPI):
        form_data = {
            "product_ID": "99999",
            "new_stock_level": "5",
            "old_stock_level": "4",
        }
        response = self.client.post(self.URL, form_data)
        self.assertEqual(404, response.status_code)
        self.assertEqual(0, len(mock_CCAPI.mock_calls))


class TestGetStockLevelView(
    InventoryViewTest, APIViewTests, fixtures.SingleProductRangeFixture
):
    fixtures = fixtures.SingleProductRangeFixture.fixtures
    URL = "/inventory/get_stock_level/"

    @patch("inventory.models.products.CCAPI")
    def test_post_method(self, mock_CCAPI):
        mock_CCAPI.get_product.return_value = Mock(stock_level=5)
        response = self.client.post(self.URL, {"product_ID": self.product.product_ID})
        expected_response = json.dumps(
            {"product_ID": self.product.product_ID, "stock_level": 5}
        ).encode("utf8")
        self.assertEqual(response.content, expected_response)
        mock_CCAPI.get_product.assert_called_once_with(self.product.product_ID)
        self.assertEqual(1, len(mock_CCAPI.mock_calls))

    @patch("inventory.models.products.CCAPI")
    def test_invalid_product_ID(self, mock_CCAPI):
        response = self.client.post(self.URL, {"product_ID": "99999"})
        self.assertEqual(404, response.status_code)
        self.assertEqual(0, len(mock_CCAPI.mock_calls))


class BaseImageViewTest(InventoryViewTest, fixtures.SingleProductRangeFixture):
    fixtures = fixtures.SingleProductRangeFixture.fixtures

    def setUp(self):
        super().setUp()
        models.ProductImage.objects.bulk_create(
            [
                models.ProductImage(
                    image_ID=str(2849393 + i),
                    product=self.product,
                    filename=f"img_{i}.jpg",
                    URL=f"http://someimages.com/img_{i}.jpg",
                    position=i - 1,
                )
                for i in range(1, 6)
            ]
        )


class TestSetImageOrderView(BaseImageViewTest, APIViewTests):
    URL = "/inventory/set_image_order/"

    @patch("inventory.models.product_image.CCAPI")
    def test_post_method(self, mock_CCAPI):
        images = models.ProductImage.objects.filter(product=self.product)
        image_order = list(reversed([image.image_ID for image in images]))
        data = {"product_ID": self.product.product_ID, "image_order": image_order}
        response = self.client.post(
            self.URL, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"ok", response.content)
        images = models.ProductImage.objects.filter(product=self.product)
        self.assertEqual(image_order, [image.image_ID for image in images])
        mock_CCAPI.set_image_order.assert_called_once_with(
            product_id=self.product.product_ID, image_ids=image_order
        )
        self.assertEqual(1, len(mock_CCAPI.mock_calls))

    @patch("inventory.models.products.CCAPI")
    def test_invalid_product_ID(self, mock_CCAPI):
        image_order = ["28493023", "38409303"]
        data = {"product_ID": "999999", "image_order": image_order}
        response = self.client.post(
            self.URL, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(500, response.status_code)
        self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.models.product_image.CCAPI")
    def test_exception_raised_for_wrong_image_IDs(self, mock_CCAPI):
        image_order = ["28493023", "38409303"]
        data = {"product_ID": self.product.product_ID, "image_order": image_order}
        response = self.client.post(
            self.URL, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(500, response.status_code)
        self.assertEqual(0, len(mock_CCAPI.mock_calls))


class TestDeleteImageView(BaseImageViewTest, APIViewTests):
    URL = "/inventory/delete_image/"

    @patch("inventory.views.api.CCAPI")
    def test_post_method(self, mock_CCAPI):
        images = models.ProductImage.objects.filter(product=self.product)
        image_ID = images[0].image_ID
        response = self.client.post(
            reverse("inventory:delete_image"),
            json.dumps({"image_id": image_ID}),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"ok", response.content)
        mock_CCAPI.delete_image.assert_called_once_with(image_ID)
        self.assertEqual(1, len(mock_CCAPI.mock_calls))
        self.assertFalse(models.ProductImage.objects.filter(image_ID=image_ID).exists())

    @patch("inventory.views.api.CCAPI")
    def test_delete_non_existant_image(self, mock_CCAPI):
        response = self.client.post(
            self.URL,
            json.dumps({"image_id": "93734948"}),
            content_type="application/json",
        )
        self.assertEqual(500, response.status_code)
        self.assertEqual(0, len(mock_CCAPI.mock_calls))
