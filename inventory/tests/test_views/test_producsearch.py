from unittest.mock import call, patch

from inventory import forms
from inventory.tests import mocks
from stcadmin.tests.stcadmin_test import ViewTests

from .test_views import InventoryViewTest


class TestProductSearchView(InventoryViewTest, ViewTests):
    URL = "/inventory/product_search/"
    template = "inventory/product_search.html"

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.forms.product_search.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

    def make_post_request(self, data=None, product_options=None, results=None):
        data = data or {}
        product_options = product_options or []
        results = results or []
        self.mock_CCAPI.get_product_options.return_value = product_options
        self.mock_CCAPI.search_products.return_value = results
        self.mock_CCAPI.get_range.side_effect = results
        return self.client.post(self.URL, data)

    def test_get_method(self):
        self.mock_CCAPI.get_product_options.return_value = []
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.mock_CCAPI.get_product_options.assert_called_once()

    def test_post_method(self):
        results = [
            mocks.MockCCAPIProductRange(id=3303384, name="Range 1"),
            mocks.MockCCAPIProductRange(id=9903839, name="Range 2"),
        ]
        search_text = "Product Name"
        data = {"search_type": "basic", "basic_search_text": search_text}
        response = self.make_post_request(
            data=data, product_options=None, results=results
        )
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_search_results(self):
        results = [
            mocks.MockCCAPIProductRange(id=3303384, name="Range 1"),
            mocks.MockCCAPIProductRange(id=9903839, name="Range 2"),
        ]
        search_text = "Product Name"
        data = {"search_type": "basic", "basic_search_text": search_text}
        response = self.make_post_request(
            data=data, product_options=None, results=results
        )
        self.mock_CCAPI.get_product_options.assert_called_once()
        self.mock_CCAPI.search_products.assert_called_once_with(search_text)
        self.mock_CCAPI.get_range.assert_has_calls(
            [call(result.id) for result in results]
        )
        self.assertEqual(response.context["product_ranges"], results)

    def test_product_option_drop_down(self):
        values = [
            mocks.MockProductOptionValue(value=name)
            for name in ("Red", "Green", "Blue")
        ]
        product_option = mocks.MockProductOption(
            option_name=forms.ProductSearchForm.selectable_options[0], values=values
        )
        response = self.make_post_request(
            data={"search_type": "basic", "basic_search_text": "Product Name"},
            product_options=[product_option],
            results=None,
        )
        self.assertIn(product_option.option_name, response.content.decode("utf8"))
        for value in values:
            self.assertIn(value.value, response.content.decode("utf8"))

    def test_unselecteable_drop_down(self):
        values = [
            mocks.MockProductOptionValue(value=name)
            for name in ("Red", "Green", "Blue")
        ]
        product_option = mocks.MockProductOption(
            option_name="Mock Product Option", values=values
        )
        response = self.make_post_request(
            data={"search_type": "basic", "basic_search_text": "Product Name"},
            product_options=[product_option],
            results=None,
        )
        self.assertNotIn(product_option.option_name, response.content.decode("utf8"))
        for value in values:
            self.assertNotIn(value.value, response.content.decode("utf8"))

    def test_invalid_search_type(self):
        data = {"search_type": "invalid_value", "basic_search_text": "search text"}
        response = self.make_post_request(data=data)
        self.assertFalse(response.context["form"].is_valid())

    def test_end_of_line_filter_include(self):
        results = [
            mocks.MockCCAPIProductRange(end_of_line=True),
            mocks.MockCCAPIProductRange(end_of_line=False),
        ]
        data = {
            "search_type": "basic",
            "basic_search_text": "search text",
            "end_of_line": "include",
        }
        response = self.make_post_request(data=data, results=results)
        self.assertIn(results[0], response.context["product_ranges"])
        self.assertIn(results[1], response.context["product_ranges"])

    def test_end_of_line_filter_exclude(self):
        results = [
            mocks.MockCCAPIProductRange(end_of_line=True),
            mocks.MockCCAPIProductRange(end_of_line=False),
        ]
        data = {
            "search_type": "basic",
            "basic_search_text": "search text",
            "end_of_line": "exclude",
        }
        response = self.make_post_request(data=data, results=results)
        self.assertNotIn(results[0], response.context["product_ranges"])
        self.assertIn(results[1], response.context["product_ranges"])

    def test_end_of_line_filter_exclusive(self):
        results = [
            mocks.MockCCAPIProductRange(end_of_line=True),
            mocks.MockCCAPIProductRange(end_of_line=False),
        ]
        data = {
            "search_type": "basic",
            "basic_search_text": "search text",
            "end_of_line": "exclusive",
        }
        response = self.make_post_request(data=data, results=results)
        self.assertIn(results[0], response.context["product_ranges"])
        self.assertNotIn(results[1], response.context["product_ranges"])

    def test_advanced_search(self):
        results = [mocks.MockCCAPIProductRange()]
        options = [
            mocks.MockProductOption(
                option_name=forms.ProductSearchForm.selectable_options[0],
                values=[mocks.MockProductOptionValue()],
            )
        ]
        data = {
            "search_type": "advanced",
            "advanced_search_text": "Search Text",
            "advanced_hide_out_of_stock": False,
            "advanced_option_0": options[0].id,
            "advanced_option_1": options[0].values[0].id,
        }
        self.mock_CCAPI.get_ranges.return_value = results
        response = self.make_post_request(
            data=data, results=results, product_options=options
        )
        self.assertEqual(response.context["product_ranges"], results)
        self.mock_CCAPI.get_ranges.assert_called_once_with(
            search_text=data["advanced_search_text"],
            only_in_stock=data["advanced_hide_out_of_stock"],
            option_matches_id=int(options[0].values[0].id),
        )

    def test_search_without_text_or_option_is_invalid(self):
        data = {"search_type": "advanced", "search_text": ""}
        self.mock_CCAPI.get_ranges.return_value = []
        response = self.make_post_request(data=data)
        self.assertFalse(response.context["form"].is_valid())
