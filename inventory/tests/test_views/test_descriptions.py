import json
from unittest.mock import patch

from inventory.tests import mocks
from stcadmin.tests.stcadmin_test import ViewTests

from .test_views import InventoryViewTest


class TestDescriptionsView(InventoryViewTest, ViewTests):
    template = "inventory/descriptions.html"

    range_id = "8946165"

    title = "New Title"
    description = "New Description\nStill good"
    bullets = ["Magenta", "Crowded", "Two", "Simple", "Crochet"]
    search_terms = ["Brown", "Apple", "Edge", "Packet", "Sound"]

    def get_URL(self, range_id=range_id):
        return f"/inventory/descriptions/{range_id}/"

    def post_data(self):
        return {
            "title": self.title,
            "description": self.description,
            "amazon_bullets": json.dumps(self.bullets),
            "search_terms": json.dumps(self.search_terms),
        }

    def setUp(self):
        super().setUp()
        cc_products_patcher = patch("inventory.views.descriptions.cc_products")
        self.mock_cc_products = cc_products_patcher.start()
        self.addCleanup(cc_products_patcher.stop)
        self.product_range = mocks.MockCCProductsProductRange()
        self.mock_cc_products.get_range.return_value = self.product_range

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_post_method(self):
        response = self.client.post(self.get_URL(), self.post_data())
        self.assertRedirects(response, self.get_URL())

    def test_description_set(self):
        self.client.post(self.get_URL(), self.post_data())
        self.assertEqual(self.description, self.product_range.description)

    def test_name_set(self):
        self.client.post(self.get_URL(), self.post_data())
        self.assertEqual(self.title, self.product_range.name)

    def test_bullets_set(self):
        self.client.post(self.get_URL(), self.post_data())
        self.assertEqual(self.bullets, self.product_range.products[0].amazon_bullets)

    def test_search_terms_set(self):
        self.client.post(self.get_URL(), self.post_data())
        self.assertEqual(
            self.search_terms, self.product_range.products[0].amazon_search_terms
        )

    def test_message_set(self):
        response = self.client.post(self.get_URL(), self.post_data(), follow=True)
        messages = list(response.context["messages"])
        self.assertEqual("Description Updated", str(messages[0]))
