from unittest.mock import patch

from inventory import models
from inventory.tests import fixtures
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestProductImage(STCAdminTest, fixtures.SingleProductRangeFixture):
    fixtures = fixtures.SingleProductRangeFixture.fixtures + (
        "inventory/product_image",
    )

    @patch("inventory.models.product_image.CCAPI")
    def test_create_object(self, mock_CCAPI):
        image_IDs = ["380929", "284930", "402928", "2948729"]
        for i, image_ID in enumerate(image_IDs):
            models.ProductImage(
                image_ID=image_ID,
                product=self.product,
                filename=image_ID + ".jpg",
                URL=f"http://image_server.com/{image_ID}.jpg",
                position=i,
            ).save()

    @patch("inventory.models.product_image.CCAPI")
    def test_update_image_order(self, mock_CCAPI):
        product = models.Product.objects.get(id=1)
        image_IDs = list(
            models.ProductImage.objects.filter(product=product).values_list(
                "image_ID", flat=True
            )
        )
        models.ProductImage.update_CC_image_order(product)
        mock_CCAPI.set_image_order.assert_called_once_with(
            product_id=product.product_ID, image_ids=image_IDs
        )
