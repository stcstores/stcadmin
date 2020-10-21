from unittest.mock import patch

from inventory import models
from inventory.tests import mocks
from stcadmin.tests.stcadmin_test import ViewTests

from .test_views import InventoryViewTest


class TestLocationsFormView(InventoryViewTest, ViewTests):
    fixtures = ("inventory/location",)
    template = "inventory/locations.html"

    range_id = "8946165"

    def get_URL(self, range_id=range_id):
        return f"/inventory/locations/{range_id}/"

    def setUp(self):
        super().setUp()
        ccproducts_patcher = patch("inventory.views.locations.cc_products")
        self.mock_cc_products = ccproducts_patcher.start()
        self.addCleanup(ccproducts_patcher.stop)

    def test_get_method(self):
        self.mock_cc_products.get_range.return_value = (
            mocks.MockCCProductsProductRange()
        )
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_post_method(self):
        warehouse = models.Warehouse.objects.all()[0]
        bay = warehouse.bay_set.all()[0]
        product_range = mocks.MockCCProductsProductRange(
            id=self.range_id,
            department=warehouse.name,
            products=[mocks.MockCCProductsProduct(bays=[bay.bay_ID])],
        )
        self.mock_cc_products.get_range.return_value = product_range
        response = self.client.post(
            self.get_URL(),
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "0",
                "form-MAX_NUM_FORMS": "1",
                "form-MIN_NUM_FORMS": "1",
                "form-0-locations": [bay.bay_ID],
                "form-0-product_id": self.range_id,
                "form-0-stock_level": 5,
            },
        )
        self.assertRedirects(response, self.get_URL())

    def test_location_updated(self):
        old_warehouse = models.Warehouse.objects.all()[0]
        old_bay = old_warehouse.bay_set.all()[0]
        new_warehouse = models.Warehouse.objects.all()[1]
        new_bay = new_warehouse.bay_set.all()[0]
        product_range = mocks.MockCCProductsProductRange(
            id=self.range_id,
            department=old_warehouse.name,
            products=[mocks.MockCCProductsProduct(bays=[old_bay.bay_ID])],
        )
        self.mock_cc_products.get_range.return_value = product_range
        response = self.client.post(
            self.get_URL(),
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "0",
                "form-MAX_NUM_FORMS": "1",
                "form-MIN_NUM_FORMS": "1",
                "form-0-locations": [new_bay.bay_ID],
                "form-0-product_id": self.range_id,
                "form-0-stock_level": 5,
            },
        )
        self.assertRedirects(response, self.get_URL())
        self.assertEqual(new_warehouse.name, product_range.products[0].department)
        self.assertEqual([new_bay.bay_ID], product_range.products[0].bays)

    def test_invalid_location(self):
        warehouse = models.Warehouse.objects.all()[0]
        bay = warehouse.bay_set.all()[0]
        product_range = mocks.MockCCProductsProductRange(
            id=self.range_id,
            department=warehouse.name,
            products=[mocks.MockCCProductsProduct(bays=[bay.bay_ID])],
        )
        self.mock_cc_products.get_range.return_value = product_range
        response = self.client.post(
            self.get_URL(),
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "0",
                "form-MAX_NUM_FORMS": "1",
                "form-MIN_NUM_FORMS": "1",
                "form-0-locations": ["99999999"],
                "form-0-product_id": self.range_id,
                "form-0-stock_level": 5,
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("locations", response.context["formset"].errors[0])
