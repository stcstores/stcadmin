from unittest.mock import Mock, patch

from inventory import forms, models
from inventory.tests import fixtures
from inventory.views import views
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests

from .inventory_view_test import InventoryViewTest


class TestInventoryUserMixin(STCAdminTest):
    def setUp(self):
        self.create_user()
        self.login_user()

    def test_valid_group(self):
        self.add_group("inventory")
        view = views.InventoryUserMixin()
        view.request = Mock(user=self.user)
        self.assertTrue(view.test_func())

    def test_invalid_group(self):
        view = views.InventoryUserMixin()
        view.request = Mock(user=self.user)
        self.assertFalse(view.test_func())


class TestSKUGeneratorView(InventoryViewTest, ViewTests):
    URL = "/inventory/sku_generator/"
    template = "inventory/sku_generator.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)


class TestCreateBayView(
    InventoryViewTest, fixtures.ProductRequirementsFixture, ViewTests
):
    fixtures = fixtures.ProductRequirementsFixture.fixtures

    URL = "/inventory/create_warehouse_bay/"
    template = "inventory/create_warehouse_bay.html"

    def get_form_data(self):
        return {
            "department": self.department.id,
            "name": "New Bay",
            "bay_type": "primary",
        }

    def make_post_request(self):
        return self.client.post(self.URL, self.get_form_data())

    @patch("inventory.models.locations.CCAPI")
    def test_get_method(self, mock_CCAPI):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertEqual(0, len(mock_CCAPI.mock_calls))

    def test_context(self):
        response = self.make_get_request()
        self.assertIsNotNone(response.context)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], forms.CreateBayForm)

    @patch("inventory.models.locations.CCAPI")
    def test_post_method(self, mock_CCAPI):
        form_data = self.get_form_data()
        new_bay_ID = "979461"
        mock_CCAPI.get_bay_id.return_value = new_bay_ID
        response = self.client.post(self.URL, form_data, follow=True)
        self.assertRedirects(response, self.URL)
        mock_CCAPI.get_bay_id.assert_called_once_with(
            form_data["name"], self.warehouse_1.name, create=True
        )
        self.assertEqual(1, len(mock_CCAPI.mock_calls))
        self.assertTrue(models.Bay.objects.filter(bay_ID=new_bay_ID).exists())
        bay = models.Bay.objects.get(bay_ID=new_bay_ID)
        self.assertEqual(form_data["name"], bay.name)
        self.assertEqual(bay.warehouse, self.warehouse_1)

    @patch("inventory.models.locations.CCAPI")
    def test_messsage_added(self, mock_CCAPI):
        form_data = self.get_form_data()
        mock_CCAPI.get_bay_id.return_value = "979461"
        response = self.client.post(self.URL, form_data, follow=True)
        self.assertIsNotNone(response.context)
        self.assertIn("messages", response.context)
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            f"Created bay {self.department.name} - {form_data['name']}",
            str(messages[0]),
        )


class TestProductSearchView(
    InventoryViewTest, fixtures.VariationProductRangeFixture, ViewTests
):
    fixtures = fixtures.VariationProductRangeFixture.fixtures

    URL = "/inventory/product_search/"
    template = "inventory/product_search/search_page.html"

    def get_form_data(self):
        return {"search_term": self.product_range.name, "show_hidden": False}

    def make_post_request(self):
        return self.client.post(self.URL, self.get_form_data())

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertIsNotNone(response.context)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], forms.ProductSearchForm)

    def test_post_method(self):
        response = self.client.post(self.URL, self.get_form_data())
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertIsNotNone(response.context)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], forms.ProductSearchForm)
        self.assertIn("product_ranges", response.context)
        self.assertEqual(list(response.context["product_ranges"]), [self.product_range])
