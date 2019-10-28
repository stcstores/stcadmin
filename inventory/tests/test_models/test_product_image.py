from unittest.mock import patch

from inventory import models
from inventory.tests import fixtures
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestProductImage(STCAdminTest, fixtures.SingleProductRangeFixture):
    fixtures = fixtures.SingleProductRangeFixture.fixtures

    @patch("inventory.models.product_image.CCAPI")
    def test_update_CC_image_order_method(self, mock_CCAPI):
        image_IDs = ["380929", "284930", "402928", "2948729"]
        for i, image_ID in enumerate(image_IDs):
            models.ProductImage(
                image_ID=image_ID,
                product=self.product,
                filename=image_ID + ".jpg",
                URL=f"http://image_server.com/{image_ID}.jpg",
                position=i,
            ).save()
        models.ProductImage.update_CC_image_order(self.product)
        mock_CCAPI.set_image_order.assert_called_once_with(
            product_id=self.product.product_ID, image_ids=image_IDs
        )
