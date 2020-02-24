import json
from unittest.mock import patch

from inventory import views
from inventory.tests import mocks
from stcadmin.tests.stcadmin_test import ViewTests

from .test_views import InventoryViewTest


class TestPrintBarcodeLabels(InventoryViewTest, ViewTests):
    template = "inventory/print_barcodes.html"

    def get_URL(self, product_id="8946165"):
        return f"/inventory/print_barcodes/{product_id}/"

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.print_barcodes.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

    def test_get_method(self):
        self.mock_CCAPI.get_range.return_value = mocks.MockCCAPIProductRange(
            products=[mocks.MockCCAPIProduct()]
        )
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.mock_CCAPI.get_range.assert_called_once()

    def test_context(self):
        product = mocks.MockCCAPIProduct(full_name="Mock Product - Red - Small")
        product_range = mocks.MockCCAPIProductRange(products=[product])
        self.mock_CCAPI.get_range.return_value = product_range
        response = self.make_get_request()
        self.assertEqual(response.context["product_range"], product_range)
        self.assertTrue(hasattr(product, "option_text"))
        self.assertEqual("Red - Small", product.option_text)


class TestBarcodePDF(InventoryViewTest, ViewTests):
    URL = "/inventory/barcode_pdf/"

    def test_post_method(self):
        response = self.client.post(self.URL, {"data": "{}"})
        self.assertEqual(200, response.status_code)
        self.assertEqual("application/pdf", response.get("content-type"))

    def test_get_label_data(self):
        input_data = [
            {"quantity": 5, "barcode": "385839839", "option_text": "Red - Small"},
            {"quantity": 3, "barcode": "651681861", "option_text": "Red - Large"},
        ]
        expected_data = [("385839839", "Red - Small") for i in range(5)] + [
            ("651681861", "Red - Large") for i in range(3)
        ]
        output_data = views.BarcodePDF().get_label_data(json.dumps(input_data))
        self.assertEqual(expected_data, output_data)
