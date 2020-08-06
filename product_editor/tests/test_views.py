import json
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.shortcuts import reverse

from inventory import models
from inventory.tests import mocks
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class InventoryViewTest(STCAdminTest):
    group_name = "inventory"

    def setUp(self):
        self.create_user()
        group = Group.objects.get(name=self.group_name)
        group.user_set.add(self.user)
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)


class ProductEditorViewTest(STCAdminTest):

    fixtures = (
        "inventory/warehouse",
        "inventory/bay",
        "inventory/department",
        "inventory/supplier",
        "inventory/package_type",
    )

    range_id = "940389403"

    group_name = "inventory"

    def setUp(self):
        self.create_user()
        group = Group.objects.get(name=self.group_name)
        group.user_set.add(self.user)
        self.login_user()
        self.setup_mocks()

    def remove_group(self):
        super().remove_group(self.group_name)

    def make_product_range(self):
        return mocks.MockCCProductsProductRange(
            id=self.range_id, department=models.Warehouse.objects.all()[0].name
        )

    def make_basic_info(self):
        warehouse = models.Warehouse.objects.all()[0]
        title = "New Product"
        description = "Product Description\nNew Product"
        bullets = ["Red", "Green", "Orange", "Blue", "Magenta"]
        search_terms = ["Large", "Medium", "Small", "XL", "XS"]
        return {
            "title": title,
            "description": description,
            "department": warehouse.warehouse_ID,
            "amazon_bullet_points": json.dumps(bullets),
            "amazon_search_terms": json.dumps(search_terms),
        }

    def make_product_info(self):
        warehouse = models.Warehouse.objects.all()[0]
        return {
            "barcode": "8491848946",
            "purchase_price": 12.99,
            "price_0": "20",
            "price_1": 20.32,
            "price_2": 22.52,
            "retail_price": 24.99,
            "stock_level": 5,
            "location_0": warehouse.warehouse_ID,
            "location_1": [warehouse.bay_set.all()[0].bay_ID],
            "supplier": models.Supplier.objects.all()[0].product_option_value_ID,
            "supplier_sku": "TY93283",
            "weight": 50,
            "dimensions_0": 125,
            "dimensions_1": 50,
            "dimensions_2": 78,
            "package_type": models.PackageType.objects.all()[0].product_option_value_ID,
            "brand": "84943",
            "manufacturer": "78188",
            "gender": "womens",
            "hs_code": "9302390",
        }

    def add_mock(self, name, path):
        patcher = patch(path)
        setattr(self, name, patcher.start())
        self.addCleanup(patcher.stop)

    def setup_mocks(self):
        pass

    def update_session(self, update):
        self.session = self.client.session
        self.session.update(update)
        self.session.save()


class TestNewBasicInfo(ProductEditorViewTest, ViewTests):

    URL = "/product_editor/basic_info/"
    template = "product_editor/basic_info.html"

    session_key = "new_product"

    def setUp(self):
        super().setUp()
        self.warehouse = models.Warehouse.objects.all()[0]
        self.title = "New Product"
        self.description = "Product Description\nNew Product"
        self.bullets = ["Red", "Green", "Orange", "Blue", "Magenta"]
        self.search_terms = ["Large", "Medium", "Small", "XL", "XS"]

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_post_method(self):
        response = self.client.post(
            self.get_URL(), {"department": self.warehouse.warehouse_ID}
        )
        self.assertRedirects(
            response,
            reverse("product_editor:product_info"),
            fetch_redirect_response=False,
        )

    def test_product_data_created_in_session(self):
        self.client.post(self.get_URL(), {"department": self.warehouse.warehouse_ID})
        self.assertIn(self.session_key, self.client.session)

    def test_basic_info_added_to_product_date(self):
        self.client.post(self.get_URL(), {"department": self.warehouse.warehouse_ID})
        self.assertIn("basic_info", self.client.session.get(self.session_key))

    def test_title_set(self):
        self.client.post(
            self.get_URL(),
            {"department": self.warehouse.warehouse_ID, "title": self.title},
        )
        product_data = self.client.session[self.session_key]
        self.assertEqual(self.title, product_data["basic_info"]["title"])

    def test_department_set(self):
        self.client.post(self.get_URL(), {"department": self.warehouse.warehouse_ID})
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            self.warehouse.warehouse_ID, product_data["basic_info"]["department"]
        )

    def test_description_set(self):
        self.client.post(
            self.get_URL(),
            {
                "department": self.warehouse.warehouse_ID,
                "description": self.description,
            },
        )
        product_data = self.client.session[self.session_key]
        self.assertEqual(self.description, product_data["basic_info"]["description"])

    def test_bullets_set(self):
        self.client.post(
            self.get_URL(),
            {
                "department": self.warehouse.warehouse_ID,
                "amazon_bullet_points": json.dumps(self.bullets),
            },
        )
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            self.bullets, product_data["basic_info"]["amazon_bullet_points"]
        )

    def test_search_terms_set(self):
        self.client.post(
            self.get_URL(),
            {
                "department": self.warehouse.warehouse_ID,
                "amazon_search_terms": json.dumps(self.bullets),
            },
        )
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            self.bullets, product_data["basic_info"]["amazon_search_terms"]
        )

    def test_error_for_no_department(self):
        response = self.client.post(self.get_URL(), {})
        self.assertIn("department", str(response.context["form"].errors))


class TestEditBasicInfo(ProductEditorViewTest, ViewTests):

    template = "product_editor/basic_info.html"

    range_id = "984646"
    session_key = "edit_product"

    def get_URL(self, range_id=None):
        range_id = range_id or self.range_id
        return f"/product_editor/basic_info/{range_id}/"

    def setUp(self):
        super().setUp()
        self.warehouse = models.Warehouse.objects.all()[0]
        self.product = mocks.MockCCProductsProductRange(
            id=self.range_id, department=self.warehouse.name
        )
        self.mock_cc_products.get_range.return_value = self.product
        self.title = "New Product"
        self.description = "Product Description\nNew Product"
        self.bullets = ["Red", "Green", "Orange", "Blue", "Magenta"]
        self.search_terms = ["Large", "Medium", "Small", "XL", "XS"]

    def setup_mocks(self):
        self.add_mock(
            "mock_cc_products",
            "product_editor.editor_manager.productloader.cc_products",
        )

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_post_method(self):
        response = self.client.post(
            self.get_URL(), {"department": self.warehouse.warehouse_ID}
        )
        self.assertRedirects(
            response,
            reverse("product_editor:product_info", args=[self.range_id]),
            fetch_redirect_response=False,
        )

    def test_product_data_created_in_session(self):
        self.client.post(self.get_URL(), {"department": self.warehouse.warehouse_ID})
        self.assertIn(self.session_key, self.client.session)

    def test_basic_info_added_to_product_date(self):
        self.client.post(self.get_URL(), {"department": self.warehouse.warehouse_ID})
        self.assertIn("basic_info", self.client.session.get(self.session_key))

    def test_title_set(self):
        self.client.post(
            self.get_URL(),
            {"department": self.warehouse.warehouse_ID, "title": self.title},
        )
        product_data = self.client.session[self.session_key]
        self.assertEqual(self.title, product_data["basic_info"]["title"])

    def test_department_set(self):
        self.client.post(self.get_URL(), {"department": self.warehouse.warehouse_ID})
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            self.warehouse.warehouse_ID, product_data["basic_info"]["department"]
        )

    def test_description_set(self):
        self.client.post(
            self.get_URL(),
            {
                "department": self.warehouse.warehouse_ID,
                "description": self.description,
            },
        )
        product_data = self.client.session[self.session_key]
        self.assertEqual(self.description, product_data["basic_info"]["description"])

    def test_bullets_set(self):
        self.client.post(
            self.get_URL(),
            {
                "department": self.warehouse.warehouse_ID,
                "amazon_bullet_points": json.dumps(self.bullets),
            },
        )
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            self.bullets, product_data["basic_info"]["amazon_bullet_points"]
        )

    def test_search_terms_set(self):
        self.client.post(
            self.get_URL(),
            {
                "department": self.warehouse.warehouse_ID,
                "amazon_search_terms": json.dumps(self.bullets),
            },
        )
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            self.bullets, product_data["basic_info"]["amazon_search_terms"]
        )

    def test_error_for_no_department(self):
        response = self.client.post(self.get_URL(), {})
        self.assertIn("department", str(response.context["form"].errors))


class TestClearNewProduct(ProductEditorViewTest, ViewTests):

    URL = "/product_editor/clear_product/"

    def test_get_method(self):
        self.client.session["basic_info"] = {"title": "Test Product"}
        self.make_get_request()
        self.assertNotIn("basic_info", self.client.session)


class TestClearEditedProduct(ProductEditorViewTest, ViewTests):

    range_id = "84938490"

    def get_URL(self, range_id=None):
        range_id = range_id or self.range_id
        return f"/product_editor/clear_product/{range_id}/"

    def setUp(self):
        super().setUp()
        ccproducts_patcher = patch(
            "product_editor.editor_manager.productloader.cc_products"
        )
        self.mock_cc_products = ccproducts_patcher.start()
        self.addCleanup(ccproducts_patcher.stop)
        self.warehouse = models.Warehouse.objects.all()[0]
        self.product = mocks.MockCCProductsProductRange(
            id=self.range_id, department=self.warehouse.name
        )
        self.mock_cc_products.get_range.return_value = self.product

    def test_get_method(self):
        self.client.session["basic_info"] = {"title": "Test Product"}
        self.make_get_request()
        self.assertNotIn("basic_info", self.client.session)


class TestNewProductInfo(ProductEditorViewTest, ViewTests):

    URL = "/product_editor/product_info/"
    session_key = "new_product"

    def setUp(self):
        super().setUp()
        self.setup_mocks()
        self.mock_CCAPI.get_product_options.return_value = mocks.MockProductOptions(
            options=[
                mocks.MockProductOption(option_name="Brand"),
                mocks.MockProductOption(option_name="Manufacturer"),
            ]
        )
        self.product_range = self.make_product_range()
        self.mock_cc_products.get_range.return_value = self.product_range
        self.update_session(
            {self.session_key: {"type": "single", "basic_info": self.make_basic_info()}}
        )

    def setup_mocks(self):
        self.add_mock(
            "mock_cc_products",
            "product_editor.editor_manager.productloader.cc_products",
        )
        self.add_mock("mock_CCAPI", "product_editor.forms.forms.CCAPI")

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed("product_editor/product_info.html")

    def test_post_method(self):
        response = self.client.post(self.get_URL(), self.make_product_info())
        self.assertRedirects(
            response,
            reverse("product_editor:listing_options"),
            fetch_redirect_response=False,
        )

    def test_back_redirect(self):
        data = self.make_product_info()
        data["back"] = True
        response = self.client.post(self.get_URL(), data)
        self.assertRedirects(
            response,
            reverse("product_editor:basic_info"),
            fetch_redirect_response=False,
        )

    def test_goto_redirect(self):
        data = self.make_product_info()
        data["goto"] = "variation_info"
        response = self.client.post(self.get_URL(), data)
        self.assertRedirects(
            response,
            reverse("product_editor:variation_info"),
            fetch_redirect_response=False,
        )

    def test_barcode_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(data["barcode"], product_data["product_info"]["barcode"])

    def test_purchase_price_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            data["purchase_price"], product_data["product_info"]["purchase_price"]
        )

    def test_price_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            {
                "vat_rate": data["price_0"],
                "ex_vat": data["price_1"],
                "with_vat_price": data["price_2"],
            },
            product_data["product_info"]["price"],
        )

    def test_retail_price_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            data["retail_price"], product_data["product_info"]["retail_price"]
        )

    def test_stock_level_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            data["stock_level"], product_data["product_info"]["stock_level"]
        )

    def test_location_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            {"warehouse": data["location_0"], "bays": data["location_1"]},
            product_data["product_info"]["location"],
        )

    def test_supplier_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(data["supplier"], product_data["product_info"]["supplier"])

    def test_supplier_sku_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            data["supplier_sku"], product_data["product_info"]["supplier_sku"]
        )

    def test_weight_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(data["weight"], product_data["product_info"]["weight"])

    def test_dimesions_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            {
                "height": data["dimensions_0"],
                "length": data["dimensions_1"],
                "width": data["dimensions_2"],
            },
            product_data["product_info"]["dimensions"],
        )

    def test_brand_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(data["brand"], product_data["product_info"]["brand"])

    def test_manufacturer_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            data["manufacturer"], product_data["product_info"]["manufacturer"]
        )

    def test_gender_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(data["gender"], product_data["product_info"]["gender"])

    def test_initial_set(self):
        data = self.make_product_info()
        self.session.update({self.session_key: {"product_info": data}})
        self.session.save()
        response = self.client.post(self.get_URL())
        self.assertDictEqual(data, response.context["form"].initial)


class TestEditProductInfo(ProductEditorViewTest, ViewTests):

    session_key = "edit_product"

    def get_URL(self):
        return f"/product_editor/product_info/{self.range_id}/"

    def setUp(self):
        super().setUp()
        self.setup_mocks()
        self.mock_CCAPI.get_product_options.return_value = mocks.MockProductOptions(
            options=[
                mocks.MockProductOption(option_name="Brand"),
                mocks.MockProductOption(option_name="Manufacturer"),
            ]
        )
        self.product_range = self.make_product_range()
        self.mock_cc_products.get_range.return_value = self.product_range
        self.update_session(
            {self.session_key: {"type": "single", "basic_info": self.make_basic_info()}}
        )

    def setup_mocks(self):
        self.add_mock(
            "mock_cc_products",
            "product_editor.editor_manager.productloader.cc_products",
        )
        self.add_mock("mock_CCAPI", "product_editor.forms.forms.CCAPI")

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed("product_editor/product_info.html")

    def test_post_method(self):
        response = self.client.post(self.get_URL(), self.make_product_info())
        self.assertRedirects(
            response,
            reverse("product_editor:listing_options", args=[self.range_id]),
            fetch_redirect_response=False,
        )

    def test_back_redirect(self):
        data = self.make_product_info()
        data["back"] = True
        response = self.client.post(self.get_URL(), data)
        self.assertRedirects(
            response,
            reverse("product_editor:basic_info", args=[self.range_id]),
            fetch_redirect_response=False,
        )

    def test_goto_redirect(self):
        data = self.make_product_info()
        data["goto"] = "variation_info"
        response = self.client.post(self.get_URL(), data)
        self.assertRedirects(
            response,
            reverse("product_editor:variation_info", args=[self.range_id]),
            fetch_redirect_response=False,
        )

    def test_barcode_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(data["barcode"], product_data["product_info"]["barcode"])

    def test_purchase_price_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            data["purchase_price"], product_data["product_info"]["purchase_price"]
        )

    def test_price_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            {
                "vat_rate": data["price_0"],
                "ex_vat": data["price_1"],
                "with_vat_price": data["price_2"],
            },
            product_data["product_info"]["price"],
        )

    def test_retail_price_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            data["retail_price"], product_data["product_info"]["retail_price"]
        )

    def test_stock_level_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            data["stock_level"], product_data["product_info"]["stock_level"]
        )

    def test_location_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            {"warehouse": data["location_0"], "bays": data["location_1"]},
            product_data["product_info"]["location"],
        )

    def test_supplier_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(data["supplier"], product_data["product_info"]["supplier"])

    def test_supplier_sku_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            data["supplier_sku"], product_data["product_info"]["supplier_sku"]
        )

    def test_weight_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(data["weight"], product_data["product_info"]["weight"])

    def test_dimesions_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            {
                "height": data["dimensions_0"],
                "length": data["dimensions_1"],
                "width": data["dimensions_2"],
            },
            product_data["product_info"]["dimensions"],
        )

    def test_brand_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(data["brand"], product_data["product_info"]["brand"])

    def test_manufacturer_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(
            data["manufacturer"], product_data["product_info"]["manufacturer"]
        )

    def test_gender_set(self):
        data = self.make_product_info()
        self.client.post(self.get_URL(), data)
        product_data = self.client.session[self.session_key]
        self.assertEqual(data["gender"], product_data["product_info"]["gender"])

    def test_initial_set(self):
        data = self.make_product_info()
        self.session.update({self.session_key: {"product_info": data}})
        self.session.save()
        response = self.client.post(self.get_URL())
        product = self.product_range.products[0]
        expected = {
            "barcode": product.barcode,
            "purchase_price": product.purchase_price,
            "supplier_sku": product.supplier_sku,
            "weight": product.weight,
            "supplier": product.supplier.factory_name,
            "brand": product.brand,
            "manufacturer": product.manufacturer,
            "retail_price": product.retail_price,
            "gender": product.gender,
            "package_type": product.package_type,
            "dimensions": {
                "width": product.width,
                "length": product.length,
                "height": product.height,
            },
            "location": {"warehouse": "", "bays": []},
            "product_id": product.id,
            "stock_level": product.stock_level,
            "price": {"ex_vat": product.price, "vat_rate": product.vat_rate},
            "hs_code": product.hs_code,
        }
        assert response.context["form"].initial == expected
