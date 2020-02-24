from unittest.mock import patch

from inventory.tests import mocks
from stcadmin.tests.stcadmin_test import ViewTests

from .test_views import InventoryViewTest


class TestProductRangeView(InventoryViewTest, ViewTests):
    template = "inventory/product_range.html"

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.productrange.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

    def get_URL(self, product_id="4839384"):
        return f"/inventory/product_range/{product_id}/"

    def test_get_method(self):
        self.mock_CCAPI.get_range.return_value = mocks.MockCCAPIProductRange()
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_context(self):
        mock_range = mocks.MockCCAPIProductRange()
        self.mock_CCAPI.get_range.return_value = mock_range
        response = self.make_get_request()
        self.assertEqual(mock_range, response.context["product_range"])

    def test_range_not_found(self):
        self.mock_CCAPI.get_range.side_effect = Exception
        response = self.make_get_request()
        self.assertEqual(404, response.status_code)
        self.assertTemplateUsed("inventory/product_range_404.html")
