import json
from unittest.mock import Mock, call, patch

from django.contrib.auth.models import Group

from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class EPOSTest(STCAdminTest):
    group_name = "epos"

    def setUp(self):
        self.create_user()
        group = Group.objects.get(name=self.group_name)
        group.user_set.add(self.user)
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)


class TestIndexView(EPOSTest, ViewTests):
    URL = "/epos/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed("epos/index.html")


class TestBarcodeSearchView(EPOSTest, ViewTests):
    URL = "/epos/barcode_search/"

    barcode = "89461656654"
    product_ID = "384938"
    product_name = "Product"
    product_SKU = "TZL-8HL-9IV"
    product_base_price = 8.70
    product_VAT_rate = 5
    product_stock_level = 5
    expected_response = {
        "id": product_ID,
        "name": product_name,
        "sku": product_SKU,
        "barcode": barcode,
        "base_price": float(product_base_price),
        "vat_rate": product_VAT_rate,
        "stock_level": product_stock_level,
        "order_quantity": 1,
    }

    def make_mock_product(self):
        return Mock(
            id=self.product_ID,
            full_name=self.product_name,
            sku=self.product_SKU,
            barcode=self.barcode,
            base_price=str(self.product_base_price),
            vat_rate=self.product_VAT_rate,
            stock_level=self.product_stock_level,
        )

    def get_form_data(self):
        return {"barcode": self.barcode}

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    @patch("epos.views.CCAPI")
    def test_get_method(self, mock_CCAPI):
        super().test_get_method()
        self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("epos.views.CCAPI")
    def test_post_method(self, mock_CCAPI):
        product = self.make_mock_product()
        search_results = [Mock(variation_id=self.product_ID)]
        mock_CCAPI.search_products.return_value = search_results
        mock_CCAPI.get_product.return_value = product
        response = self.make_post_request()
        self.assertEqual(200, response.status_code)
        mock_CCAPI.search_products.assert_called_once_with(self.barcode)
        mock_CCAPI.get_product.assert_called_once_with(self.product_ID)
        self.assertEqual(2, len(mock_CCAPI.mock_calls))
        self.assertEqual(
            json.dumps(self.expected_response), response.content.decode("utf-8")
        )

    @patch("epos.views.CCAPI")
    def test_empty_response(self, mock_CCAPI):
        mock_CCAPI.search_products.return_value = []
        response = self.make_post_request()
        self.assertEqual(200, response.status_code)
        mock_CCAPI.search_products.assert_called_once_with(self.barcode)
        self.assertEqual(1, len(mock_CCAPI.mock_calls))
        self.assertEqual(b"Not Found", response.content)

    @patch("epos.views.CCAPI")
    def test_multiple_results(self, mock_CCAPI):
        product = self.make_mock_product()
        search_results = [
            Mock(variation_id=self.product_ID),
            Mock(variation_id="481614"),
            Mock(variation_id="89461"),
        ]
        mock_CCAPI.search_products.return_value = search_results
        mock_CCAPI.get_product.return_value = product
        response = self.make_post_request()
        self.assertEqual(200, response.status_code)
        mock_CCAPI.search_products.assert_called_once_with(self.barcode)
        mock_CCAPI.get_product.assert_called_once_with(self.product_ID)
        self.assertEqual(2, len(mock_CCAPI.mock_calls))
        self.assertEqual(
            json.dumps(self.expected_response), response.content.decode("utf-8")
        )


class TestEPOSOrderView(EPOSTest, ViewTests):

    URL = "/epos/epos_order/"

    def get_form_data(self):
        return {
            "3894930": {"stock_level": "5", "order_quantity": "2"},
            "9115664": {"stock_level": "12", "order_quantity": "5"},
        }

    def make_post_request(self):
        return self.client.post(
            self.get_URL(),
            json.dumps(self.get_form_data()),
            content_type="application/json",
        )

    @patch("epos.views.CCAPI")
    def test_post_method(self, mock_CCAPI):
        response = self.make_post_request()
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"ok", response.content)
        calls = [
            call(product_id="3894930", old_stock_level="5", new_stock_level=3),
            call(product_id="9115664", old_stock_level="12", new_stock_level=7),
        ]
        mock_CCAPI.update_product_stock_level.assert_has_calls(calls)
        self.assertEqual(2, len(mock_CCAPI.mock_calls))

    @patch("epos.views.CCAPI")
    def test_get_method(self, mock_CCAPI):
        super().test_get_method()
        self.assertEqual(0, len(mock_CCAPI.mock_calls))
