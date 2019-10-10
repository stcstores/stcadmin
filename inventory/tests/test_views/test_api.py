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
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        InventoryViewTest.setUpTestData()

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
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        InventoryViewTest.setUpTestData()

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


class BaseImageViewTest(SetupSingleProductRange, InventoryViewTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        InventoryViewTest.setUpTestData()
        models.ProductImage.objects.bulk_create(
            [
                models.ProductImage(
                    image_ID=str(2849393 + i),
                    product=cls.product,
                    filename=f"img_{i}.jpg",
                    URL=f"http://someimages.com/img_{i}.jpg",
                    position=i - 1,
                )
                for i in range(1, 6)
            ]
        )

    def setUp(self):
        SetupSingleProductRange.setUp(self)
        InventoryViewTest.setUp(self)


class TestSetImageOrderView(BaseImageViewTest):
    @patch("inventory.models.product_image.CCAPI")
    def test_post_method(self, mock_CCAPI):
        images = models.ProductImage.objects.filter(product=self.product)
        image_order = list(reversed([image.image_ID for image in images]))
        data = {"product_ID": self.product.product_ID, "image_order": image_order}
        response = self.client.post(
            reverse("inventory:set_image_order"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"ok", response.content)
        images = models.ProductImage.objects.filter(product=self.product)
        self.assertEqual(image_order, [image.image_ID for image in images])
        mock_CCAPI.set_image_order.assert_called_once_with(
            product_id=self.product.product_ID, image_ids=image_order
        )
        self.assertEqual(1, len(mock_CCAPI.mock_calls))

    @patch("inventory.models.product_image.CCAPI")
    def test_exception_raised_for_wrong_image_IDs(self, mock_CCAPI):
        image_order = ["28493023", "38409303"]
        data = {"product_ID": self.product.product_ID, "image_order": image_order}
        response = self.client.post(
            reverse("inventory:set_image_order"),
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(500, response.status_code)


class TestDeleteImageView(BaseImageViewTest):
    @patch("inventory.views.api.CCAPI")
    def test_delete_image(self, mock_CCAPI):
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
            reverse("inventory:delete_image"),
            json.dumps({"image_id": "93734948"}),
            content_type="application/json",
        )
        self.assertEqual(500, response.status_code)
