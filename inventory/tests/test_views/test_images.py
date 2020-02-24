from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile

from inventory.tests import mocks
from stcadmin.tests.stcadmin_test import ViewTests

from .test_views import InventoryViewTest


class TestImageFormView(InventoryViewTest, ViewTests):
    template = "inventory/images.html"

    range_id = "8946165"

    def get_URL(self, range_id=range_id):
        return f"/inventory/images/{range_id}/"

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.images.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

    def test_get_method(self):
        self.mock_CCAPI.get_range.return_value = mocks.MockCCAPIProductRange()
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_post_method(self):
        self.mock_CCAPI.get_range.return_value = mocks.MockCCAPIProductRange()
        data = {"product_ids": [self.range_id]}
        response = self.client.post(self.get_URL(), data)
        self.assertRedirects(response, self.get_URL())

    def test_context(self):
        range_options = mocks.MockCCAPIProductRangeOptions(
            options=[
                mocks.MockProductOption(option_name="Size", is_web_shop_select=True),
                mocks.MockProductOption(option_name="Colour", is_web_shop_select=False),
            ]
        )
        product_options = [
            mocks.MockCCAPIProductProductOption(
                option_name="Size",
                value=mocks.MockProductOptionValue(value="Small", option_name="Size"),
            ),
            mocks.MockCCAPIProductProductOption(
                option_name="Colour",
                value=mocks.MockProductOptionValue(value="Colour", option_name="Red"),
            ),
        ]
        product = mocks.MockCCAPIProduct(options=product_options)
        product_range = mocks.MockCCAPIProductRange(
            products=[product], options=range_options
        )
        self.mock_CCAPI.get_range.return_value = product_range
        response = self.make_get_request()
        self.assertEqual({"Size": "Small"}, response.context["options"])
        self.assertEqual(product_range, response.context["product_range"])
        self.assertEqual([product], response.context["products"])
        self.assertEqual([], product.images)

    def test_add_images(self):
        self.mock_CCAPI.get_range.return_value = mocks.MockCCAPIProductRange()
        with open(Path(__file__).parent / "test_image.jpg", "rb") as f:
            image = SimpleUploadedFile(
                "test_image.jpg", f.read(), content_type="image/jpg"
            )
            data = {"product_ids": [self.range_id], "cloud_commerce_images": [image]}
            response = self.client.post(self.get_URL(), data=data)
            self.mock_CCAPI.upload_image.assert_called_once()
        self.assertRedirects(response, self.get_URL())
