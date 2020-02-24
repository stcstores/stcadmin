from unittest.mock import patch

from inventory import models
from inventory.tests import mocks
from stcadmin.tests.stcadmin_test import ViewTests

from .test_views import InventoryViewTest


class TestProductView(InventoryViewTest, ViewTests):
    fixtures = ("inventory/location",)
    template = "inventory/product.html"

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("inventory.views.product.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)
        cc_products_patcher = patch("inventory.views.product.cc_products")
        self.mock_cc_products = cc_products_patcher.start()
        self.addCleanup(cc_products_patcher.stop)
        fields_ccapi_patcher = patch("product_editor.forms.fields.CCAPI")
        self.mock_fields_CCAPI = fields_ccapi_patcher.start()
        self.addCleanup(fields_ccapi_patcher.stop)

    def get_URL(self, product_id="4839384"):
        return f"/inventory/product/{product_id}/"

    def test_get_method(self):
        self.mock_CCAPI.get_product_options.return_value = [mocks.MockProductOption()]
        self.mock_fields_CCAPI.get_product_options.return_value = [
            mocks.MockProductOption()
        ]
        self.mock_cc_products.get_product.return_value = mocks.MockCCProductsProduct()
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_post_method(self):
        options = [mocks.MockProductOption(values=[mocks.MockProductOptionValue()])]
        self.mock_CCAPI.get_product_options.return_value = options
        self.mock_fields_CCAPI.get_product_options.return_value = options
        self.mock_cc_products.get_product.return_value = mocks.MockCCProductsProduct(
            options=options,
            product_range=mocks.MockCCProductsProductRange(
                options=mocks.MockCCProductsRangeOptions(
                    selected_options=[
                        mocks.MockCCProductsRangeSelectedOption(
                            name=options[0].option_name
                        )
                    ]
                )
            ),
        )
        bay = models.Bay.objects.all()[0]
        data = {
            "price_0": 20,
            "price_1": 5.50,
            "price_2": 6.80,
            "location_0": bay.warehouse.warehouse_ID,
            "location_1": bay.bay_ID,
            f"opt_{options[0].option_name}": ["Green"],
        }
        response = self.client.post(self.get_URL(), data)
        self.assertRedirects(response, self.get_URL())

    def test_context(self):
        warehouse = models.Warehouse.objects.all()[0]
        mock_product = mocks.MockCCProductsProduct(department=warehouse.name)
        self.mock_CCAPI.get_product_options.return_value = [mocks.MockProductOption()]
        self.mock_cc_products.get_product.return_value = mock_product
        response = self.make_get_request()
        self.assertEqual(mock_product, response.context["product"])
        self.assertEqual(mock_product.product_range, response.context["product_range"])
        self.assertEqual(
            list(warehouse.bay_set.all()), response.context["warehouse_bays"]
        )

    def test_context_no_bay(self):
        mock_product = mocks.MockCCProductsProduct(department="Non Existant")
        self.mock_CCAPI.get_product_options.return_value = [mocks.MockProductOption()]
        self.mock_cc_products.get_product.return_value = mock_product
        response = self.make_get_request()
        self.assertEqual([], response.context["warehouse_bays"])

    def test_range_not_found(self):
        self.mock_CCAPI.get_product_options.return_value = [mocks.MockProductOption()]
        self.mock_cc_products.get_product.side_effect = Exception
        with self.assertRaises(Exception):
            self.make_get_request()

    def test_mixed_bays(self):
        bays = list(models.Bay.objects.values_list("bay_ID", flat=True))
        product = mocks.MockCCProductsProduct(bays=bays)
        self.mock_CCAPI.get_product_options.return_value = [mocks.MockProductOption()]
        self.mock_cc_products.get_product.return_value = product
        bay = models.Bay.objects.all()[0]
        data = {
            "price_0": 20,
            "price_1": 5.50,
            "price_2": 6.80,
            "location_0": bay.warehouse.warehouse_ID,
            "location_1": bay.bay_ID,
        }
        response = self.client.post(self.get_URL(), data)
        self.assertIn("location", response.context["form"].errors)
