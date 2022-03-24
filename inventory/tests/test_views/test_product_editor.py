import json
from decimal import Decimal
from unittest.mock import Mock, patch

from django.contrib.messages import get_messages
from django.shortcuts import reverse

from inventory import forms, models
from inventory.forms.base import ProductEditorBase
from inventory.tests import fixtures
from stcadmin.tests.stcadmin_test import ViewTests

from .test_views import InventoryViewTest


class TestContinueView(InventoryViewTest, fixtures.MultipleRangesFixture, ViewTests):
    fixtures = fixtures.MultipleRangesFixture.fixtures
    URL = "/inventory/continue/"
    RANGE_ID = "384934"

    def setUp(self):
        super().setUp()
        self.other_user = self.create_user(username="second_user")
        models.ProductEdit.create_product_edit(self.user, self.normal_range)
        models.ProductEdit.create_product_edit(self.other_user, self.eol_range)
        models.ProductEdit.create_product_edit(self.other_user, self.hidden_range)

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "inventory/product_editor/continue.html")

    def test_view_context(self):
        response = self.client.get(self.URL)
        user_edits = list(models.ProductEdit.objects.filter(user=self.user))
        self.assertEqual(1, len(user_edits))
        self.assertCountEqual(user_edits, list(response.context["user_edits"]))
        other_user_edits = list(models.ProductEdit.objects.filter(user=self.other_user))
        self.assertEqual(2, len(other_user_edits))
        self.assertCountEqual(other_user_edits, list(response.context["others_edits"]))

    def test_view_with_no_user_edits(self):
        models.ProductEdit.objects.filter(user=self.user).update(user=self.other_user)
        response = self.client.get(self.URL)
        self.assertEqual(0, len(response.context["user_edits"]))
        self.assertEqual(3, len(response.context["others_edits"]))

    def test_no_other_user_edits(self):
        models.ProductEdit.objects.filter(user=self.other_user).update(user=self.user)
        response = self.client.get(self.URL)
        self.assertEqual(3, len(response.context["user_edits"]))
        self.assertEqual(0, len(response.context["others_edits"]))


class TestStartEditingProductView(
    InventoryViewTest, fixtures.VariationProductRangeFixture, ViewTests
):
    fixtures = fixtures.VariationProductRangeFixture.fixtures

    def get_URL(self):
        return f"/inventory/edit_product/{self.product_range.range_ID}/"

    def test_get_method(self):
        self.assertFalse(models.ProductEdit.objects.filter().exists())
        response = self.make_get_request()
        edit = models.ProductEdit.objects.get(product_range=self.product_range)
        self.assertRedirects(
            response, reverse("inventory:edit_product", kwargs={"edit_ID": edit.id})
        )

    def test_post_method(self):
        self.assertFalse(models.ProductEdit.objects.filter().exists())
        response = self.make_post_request()
        edit = models.ProductEdit.objects.get(product_range=self.product_range)
        self.assertRedirects(
            response, reverse("inventory:edit_product", kwargs={"edit_ID": edit.id})
        )

    def test_uses_existing_edit_if_possible(self):
        edit = models.ProductEdit.create_product_edit(self.user, self.product_range)
        response = self.make_get_request()
        edit = models.ProductEdit.objects.get(product_range=self.product_range)
        self.assertRedirects(
            response, reverse("inventory:edit_product", kwargs={"edit_ID": edit.id})
        )


class TestStartNewProductView(
    InventoryViewTest, fixtures.ProductRequirementsFixture, ViewTests
):
    fixtures = fixtures.ProductRequirementsFixture.fixtures
    URL = "/inventory/start_new_product/"

    title = "New Test Range"
    search_terms = ["A", "Test", "Item"]
    amazon_bullets = ["This", "Is", "a", "New", "Item"]
    description = "A description.\nOf a new item."

    def get_form_data(self):
        return {
            "title": self.title,
            "department": self.department.id,
            "description": self.description,
            "search_terms": json.dumps(self.search_terms),
            "amazon_bullets": json.dumps(self.amazon_bullets),
        }

    def get_ID_from_URL(self, url):
        return int(list(filter(None, url.split("/")))[-1])

    def make_post_request(self):
        return self.client.post(self.URL, self.get_form_data())

    def test_get_method(self):
        response = self.make_get_request()
        self.assertTemplateUsed(response, "inventory/product_editor/range_form.html")
        self.assertEqual(200, response.status_code)
        self.assertIsInstance(response.context["form"], forms.CreateRangeForm)

    def test_post_method(self):
        self.assertFalse(models.ProductEdit.objects.filter().exists())
        self.assertFalse(models.PartialProductRange.objects.filter().exists())
        response = self.make_post_request()
        if response.context is not None:
            form = response.context["form"]
            self.assertEqual(
                0, len(form.errors), f"Form contains errors: {form.errors}."
            )
        self.assertTrue(models.ProductEdit.objects.filter().exists())
        edit = models.ProductEdit.objects.get(user=self.user)
        self.assertRedirects(
            response, reverse("inventory:setup_variations", kwargs={"edit_ID": edit.pk})
        )

    def test_edit_created(self):
        response = self.make_post_request()
        edit_ID = self.get_ID_from_URL(response.url)
        edit = models.ProductEdit.objects.get(id=edit_ID)
        self.assertEqual(self.user, edit.user)
        self.assertIsInstance(edit.partial_product_range, models.PartialProductRange)
        self.assertIsNone(edit.product_range)
        self.assertEqual(0, edit.product_option_values.count())

    def test_product_range_created(self):
        response = self.make_post_request()
        edit_ID = self.get_ID_from_URL(response.url)
        edit = models.ProductEdit.objects.get(id=edit_ID)
        self.assertEqual(self.title, edit.partial_product_range.name)
        self.assertEqual(self.department, edit.partial_product_range.department)
        self.assertEqual(self.description, edit.partial_product_range.description)
        self.assertEqual(
            "|".join(self.search_terms), edit.partial_product_range.search_terms
        )
        self.assertEqual(
            "|".join(self.amazon_bullets),
            edit.partial_product_range.bullet_points,
        )

    def test_post_without_title(self):
        form_data = self.get_form_data()
        form_data.pop("title")
        response = self.client.post(self.URL, form_data)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.context.get("form"))
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_post_without_department(self):
        form_data = self.get_form_data()
        form_data.pop("department")
        response = self.client.post(self.URL, form_data)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.context.get("form"))
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("department", form.errors)

    def test_post_without_description(self):
        form_data = self.get_form_data()
        form_data.pop("description")
        response = self.client.post(self.URL, form_data)
        self.assertEqual(302, response.status_code)
        edit_ID = self.get_ID_from_URL(response.url)
        edit = models.ProductEdit.objects.get(id=edit_ID)
        self.assertEqual(edit.partial_product_range.description, "")

    def test_post_without_search_terms(self):
        form_data = self.get_form_data()
        form_data.pop("search_terms")
        response = self.client.post(self.URL, form_data)
        self.assertEqual(302, response.status_code)
        edit_ID = self.get_ID_from_URL(response.url)
        product_range = models.ProductEdit.objects.get(id=edit_ID).partial_product_range
        self.assertEqual(product_range.search_terms, "")

    def test_post_without_amazon_bullets(self):
        form_data = self.get_form_data()
        form_data.pop("amazon_bullets")
        response = self.client.post(self.URL, form_data)
        self.assertEqual(302, response.status_code)
        edit_ID = self.get_ID_from_URL(response.url)
        edit = models.ProductEdit.objects.get(id=edit_ID)
        self.assertEqual(edit.partial_product_range.bullet_points, "")


class TestEditProductView(InventoryViewTest, fixtures.EditingProductFixture, ViewTests):
    fixtures = fixtures.EditingProductFixture.fixtures

    def expected_variation_matrix(self):
        return {
            (
                self.large_product_option_value,
                self.red_product_option_value,
            ): models.PartialProduct.objects.get(id=7),
            (
                self.medium_product_option_value,
                self.blue_product_option_value,
            ): models.PartialProduct.objects.get(id=6),
            (
                self.small_product_option_value,
                self.red_product_option_value,
            ): models.PartialProduct.objects.get(id=1),
            (
                self.large_product_option_value,
                self.blue_product_option_value,
            ): models.PartialProduct.objects.get(id=9),
            (
                self.large_product_option_value,
                self.green_product_option_value,
            ): models.PartialProduct.objects.get(id=8),
            (
                self.medium_product_option_value,
                self.red_product_option_value,
            ): models.PartialProduct.objects.get(id=4),
            (
                self.small_product_option_value,
                self.green_product_option_value,
            ): models.PartialProduct.objects.get(id=2),
            (
                self.medium_product_option_value,
                self.green_product_option_value,
            ): models.PartialProduct.objects.get(id=5),
            (
                self.small_product_option_value,
                self.blue_product_option_value,
            ): models.PartialProduct.objects.get(id=3),
        }

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/edit_product/{edit_ID}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertTemplateUsed(response, "inventory/product_editor/edit_product.html")

    def test_get_variation_matrix(self):
        response = self.make_get_request()
        self.assertEqual(
            self.expected_variation_matrix(), response.context["variations"]
        )

    def test_variation_matrix_with_missing_product(self):
        expected = self.expected_variation_matrix()
        self.product.delete()
        variation = (self.small_product_option_value, self.red_product_option_value)
        expected[variation] = None
        response = self.make_get_request()
        self.assertEqual(expected, response.context["variations"])

    def test_context(self):
        response = self.make_get_request()
        self.assertEqual(self.product_edit, response.context["edit"])
        self.assertEqual(
            self.product_edit.partial_product_range, response.context["product_range"]
        )
        self.assertEqual(
            self.expected_variation_matrix(), response.context["variations"]
        )
        self.assertTrue(self.product_edit, response.context["ready_to_save"])

    def test_missing_variations(self):
        models.PartialProductOptionValueLink.objects.get(id=1).delete()
        response = self.make_get_request()
        self.assertRedirects(
            response,
            reverse(
                "inventory:set_product_option_values",
                kwargs={"edit_ID": self.product_edit.id},
            ),
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Variations are missing product options.")

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestSetupVariationsView(
    InventoryViewTest, fixtures.ProductRequirementsFixture, ViewTests
):
    fixtures = fixtures.ProductRequirementsFixture.fixtures + (
        "inventory/setup_variations",
    )

    template = "inventory/product_editor/setup_variations.html"

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/setup_variations/{edit_ID}/"

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.form_data)

    def setUp(self):
        super().setUp()
        self.product_edit = models.ProductEdit.objects.get(id=1)
        self.product_range = self.product_edit.partial_product_range
        self.form_data = {
            str(self.colour_product_option.pk): [
                self.red_product_option_value.value,
                self.green_product_option_value.value,
                self.blue_product_option_value.value,
            ],
            str(self.size_product_option.pk): [
                self.small_product_option_value.value,
                self.medium_product_option_value.value,
                self.large_product_option_value.value,
            ],
        }

    def test_get_method(self):
        response = self.make_get_request()
        self.assertTemplateUsed(response, self.template)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], forms.SetupVariationsForm)

    def test_context(self):
        response = self.make_get_request()
        self.assertIn("edit", response.context)
        self.assertEqual(self.product_edit, response.context["edit"])

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse(
                "inventory:create_initial_variation",
                kwargs={"edit_ID": self.product_edit.id, "product_ID": 1},
            ),
        )

    def test_product_range_selected_options_set(self):
        self.make_post_request()
        for option in (self.colour_product_option, self.size_product_option):
            self.assertTrue(
                models.PartialProductRangeSelectedOption.objects.filter(
                    product_range=self.product_range, product_option=option
                ).exists()
            )

    def test_product_option_values_added_to_edit(self):
        self.make_post_request()
        product_option_values = (
            self.small_product_option_value,
            self.medium_product_option_value,
            self.large_product_option_value,
            self.red_product_option_value,
            self.green_product_option_value,
            self.blue_product_option_value,
        )
        self.assertCountEqual(
            product_option_values, list(self.product_edit.product_option_values.all())
        )

    def test_create_single_product(self):
        response = self.client.post(self.get_URL(), {})
        self.assertRedirects(
            response,
            reverse(
                "inventory:create_initial_variation",
                kwargs={"edit_ID": self.product_edit.id, "product_ID": 1},
            ),
        )
        self.assertFalse(
            models.PartialProductOptionValueLink.objects.filter(
                product__product_range=self.product_range
            ).exists()
        )

    def test_new_product_option_value(self):
        form_data = {
            str(self.colour_product_option.pk): [
                self.red_product_option_value.value,
                "Cyan",
            ]
        }
        with self.assertRaises(NotImplementedError):
            self.client.post(self.get_URL(), form_data)

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestCreateInitialVariationView(
    InventoryViewTest, fixtures.ProductRequirementsFixture, ViewTests
):
    fixtures = fixtures.ProductRequirementsFixture.fixtures + (
        "inventory/create_initial_variation",
    )

    template = "inventory/product_editor/edit_variation.html"

    def get_URL(self, edit_ID=None, product_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        if product_ID is None:
            product_ID = self.product.id
        return "/inventory/create_initial_variation/" f"{edit_ID}/{product_ID}/"

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.form_data)

    def setUp(self):
        super().setUp()
        self.product_edit = models.ProductEdit.objects.get(id=1)
        self.product_range = self.product_edit.partial_product_range
        self.product = models.PartialProduct.objects.get(id=1)
        self.form_data = {
            ProductEditorBase.BRAND: self.brand.id,
            ProductEditorBase.MANUFACTURER: self.manufacturer.id,
            ProductEditorBase.BARCODE: "29485839",
            ProductEditorBase.SUPPLIER_SKU: "TV009",
            ProductEditorBase.SUPPLIER: self.supplier.id,
            ProductEditorBase.PURCHASE_PRICE: 5.60,
            ProductEditorBase.VAT_RATE: self.VAT_rate.id,
            ProductEditorBase.PRICE: 6.80,
            ProductEditorBase.RETAIL_PRICE: 12.70,
            ProductEditorBase.LOCATION + "_0": self.warehouse_1.id,
            ProductEditorBase.LOCATION + "_1": [self.warehouse_1_bay_1.id],
            ProductEditorBase.PACKAGE_TYPE: self.package_type.id,
            ProductEditorBase.INTERNATIONAL_SHIPPING: self.international_shipping.id,
            ProductEditorBase.WEIGHT: 500,
            ProductEditorBase.DIMENSIONS + "_0": 50,
            ProductEditorBase.DIMENSIONS + "_1": 150,
            ProductEditorBase.DIMENSIONS + "_2": 24,
            ProductEditorBase.GENDER: self.gender.id,
        }

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertEqual(self.product_edit, response.context["edit"])
        self.assertEqual(self.product_range, response.context["product_range"])
        self.assertEqual(self.product, response.context["product"])
        self.assertIsInstance(response.context["form"], forms.ProductForm)

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse("inventory:edit_product", kwargs={"edit_ID": self.product_edit.id}),
        )

    def test_new_products(self):
        self.make_post_request()
        product_query = models.PartialProduct.objects.filter(
            product_range=self.product_range
        )
        self.assertEqual(9, product_query.count())
        products = product_query.all()
        SKUs = [_.SKU for _ in products]
        self.assertEqual(len(SKUs), len(set(SKUs)))
        for product in products:
            if product.id == 1:
                self.assertEqual("29485839", product.barcode)
            self.assertEqual(self.brand, product.brand)
            self.assertEqual(self.manufacturer, product.manufacturer)
            self.assertEqual("TV009", product.supplier_SKU)
            self.assertEqual(self.supplier, product.supplier)
            self.assertEqual(Decimal("5.60"), product.purchase_price)
            self.assertEqual(self.VAT_rate, product.VAT_rate)
            self.assertEqual(Decimal("6.80"), product.price)
            self.assertEqual(Decimal("12.70"), product.retail_price)
            self.assertEqual([self.warehouse_1_bay_1], list(product.bays.all()))
            self.assertEqual(self.package_type, product.package_type)
            self.assertEqual(
                self.international_shipping, product.international_shipping
            )
            self.assertEqual(500, product.weight_grams)
            self.assertEqual(50, product.height_mm)
            self.assertEqual(150, product.length_mm)
            self.assertEqual(24, product.width_mm)
            self.assertEqual(self.gender, product.gender)
            for product_option in (
                self.size_product_option,
                self.colour_product_option,
            ):
                self.assertTrue(
                    models.PartialProductOptionValueLink.objects.filter(
                        product_option_value__product_option=product_option,
                        product=product,
                    ).exists()
                )

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="999999", product_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="999999", product_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestEditVariationsView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/edit_variations/{edit_ID}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(
            response, "inventory/product_editor/edit_variations.html"
        )

    def test_context(self):
        response = self.make_get_request()
        self.assertEqual(self.product_edit, response.context["edit"])
        self.assertEqual(self.product_range, response.context["product_range"])
        self.assertEqual(
            [self.size_product_option, self.colour_product_option],
            list(response.context["variation_options"]),
        )
        self.assertEqual(
            [self.model_product_option], list(response.context["listing_options"])
        )
        self.assertCountEqual(
            self.used_product_option_values, list(response.context["values"])
        )
        self.assertCountEqual(
            self.used_product_options, list(response.context["pre_existing_options"])
        )
        self.assertCountEqual(
            self.used_product_option_values, list(response.context["used_values"])
        )

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)


class TestEditRangeDetailsView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/range_form/{edit_ID}/"

    TITLE_VALUE = "Updated Title"
    DESCRIPTION_VALUE = "Updated description.\nOf a product."
    AMAZON_BULLETS_VALUE = ["One", "Two", "Three"]
    SEARCH_TERMS_VALUE = ["Four", "Five", "Six"]

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "inventory/product_editor/range_form.html")

    def test_context(self):
        response = response = self.make_get_request()
        self.assertEqual(self.product_edit, response.context["edit"])
        self.assertEqual(self.product_range, response.context["product_range"])
        self.assertIsInstance(response.context["form"], forms.CreateRangeForm)

    def test_post_method(self):
        form_data = {
            "title": self.TITLE_VALUE,
            "department": self.second_department.id,
            "description": self.DESCRIPTION_VALUE,
            "amazon_bullets": json.dumps(self.AMAZON_BULLETS_VALUE),
            "search_terms": json.dumps(self.SEARCH_TERMS_VALUE),
        }
        response = self.client.post(self.get_URL(), form_data)
        self.assertRedirects(
            response,
            reverse("inventory:edit_product", kwargs={"edit_ID": self.product_edit.pk}),
        )
        product_range = models.PartialProductRange.objects.get(id=1)
        self.assertEqual(self.TITLE_VALUE, product_range.name)
        self.assertEqual(self.second_department, product_range.department)
        self.assertEqual(self.DESCRIPTION_VALUE, product_range.description)
        self.assertEqual(
            "|".join(self.AMAZON_BULLETS_VALUE), product_range.bullet_points
        )
        self.assertEqual("|".join(self.SEARCH_TERMS_VALUE), product_range.search_terms)

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class AddProductOptionViewTests(fixtures.EditingProductFixture):
    fixtures = fixtures.EditingProductFixture.fixtures

    TITLE_VALUE = "Updated Title"
    DESCRIPTION_VALUE = "Updated description.\nOf a product."
    AMAZON_BULLETS_VALUE = ["One", "Two", "Three"]
    SEARCH_TERMS_VALUE = ["Four", "Five", "Six"]

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def get_form_data(self):
        return {
            "option": self.design_product_option.id,
            f"values_{self.design_product_option.id}": [
                self.cat_product_option_value.value,
                self.dog_product_option_value.value,
                self.horse_product_option_value.value,
            ],
        }

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(
            response, "inventory/product_editor/add_product_option.html"
        )

    def test_context(self):
        response = self.make_get_request()
        self.assertEqual(self.product_edit, response.context["edit"])
        self.assertEqual(self.product_range, response.context["product_range"])
        self.assertEqual(self.name_value, response.context["name"])
        self.assertIsInstance(response.context["form"], forms.AddProductOption)

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse("inventory:edit_product", kwargs={"edit_ID": self.product_edit.pk}),
            status_code=302,
            target_status_code=302,
        )
        self.assertEqual(
            1,
            models.PartialProductRangeSelectedOption.objects.filter(
                product_range=self.product_range,
                product_option=self.design_product_option,
            ).count(),
        )
        selected_option = models.PartialProductRangeSelectedOption.objects.get(
            product_range=self.product_range, product_option=self.design_product_option
        )
        self.assertEqual(self.expected_variation_value, selected_option.variation)
        for value in (
            self.cat_product_option_value,
            self.dog_product_option_value,
            self.horse_product_option_value,
        ):
            self.assertIn(value, self.product_edit.product_option_values.all())

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestAddDropdownView(AddProductOptionViewTests, InventoryViewTest, ViewTests):
    expected_variation_value = True
    name_value = "Dropdown"

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/add_dropdown/{edit_ID}/"


class TestAddListingOptionView(AddProductOptionViewTests, InventoryViewTest, ViewTests):
    expected_variation_value = False
    name_value = "Listing Option"

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/add_listing_option/{edit_ID}/"


class TestSetProductOptionValuesView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/set_product_option_values/{edit_ID}/"

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def get_form_data(self):
        products = self.variations
        form_data = {"form-TOTAL_FORMS": len(products), "form-INITIAL_FORMS": 0}
        for i, product in enumerate(products):
            form_data[f"form-{i}-product_ID"] = product.id
            for option, value in product.variation().items():
                form_data[f"form-{i}-option_{option.name}"] = value.id
            form_data[
                f"form-{i}-option_{self.model_product_option.name}"
            ] = self.model_product_option_value.id
        return form_data

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(
            response, "inventory/product_editor/set_product_option_values.html"
        )

    def test_context(self):
        response = self.make_get_request()
        self.assertEqual(self.product_edit, response.context["edit"])
        self.assertEqual(self.product_range, response.context["product_range"])
        self.assertIsInstance(
            response.context["formset"], forms.SetProductOptionValuesFormset
        )

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse("inventory:edit_product", kwargs={"edit_ID": self.product_edit.id}),
        )

    def test_product_option_value_links_updated(self):
        form_data = self.get_form_data()
        query = models.PartialProductOptionValueLink.objects.filter(
            product=self.product, product_option_value=self.small_product_option_value
        )
        self.assertTrue(query.exists())
        query.delete()
        self.assertFalse(query.exists())
        self.client.post(self.get_URL(), form_data)
        self.assertTrue(query.exists())

    def test_redirects_for_invalid_form(self):
        form_data = self.get_form_data()
        form_data.pop("form-1-product_ID")
        response = self.client.post(self.get_URL(), form_data)
        self.assertEqual(200, response.status_code)
        self.assertIn(
            {"product_ID": ["This field is required."]},
            response.context["formset"].errors,
        )

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestRemoveDropdownView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None, product_option_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        if product_option_ID is None:
            product_option_ID = self.colour_product_option.id
        return f"/inventory/remove_dowpdown/{edit_ID}/{product_option_ID}/"

    def setUp(self):
        super().setUp()
        for product in self.variations[:3]:
            product.pre_existing = False
            product.save()
        product_option = self.colour_product_option
        selected_option = models.PartialProductRangeSelectedOption.objects.get(
            product_option=product_option
        )
        selected_option.pre_existing = False
        selected_option.save()

    def test_get_method(self):
        response = self.make_get_request()
        self.assertRedirects(
            response,
            reverse(
                "inventory:edit_variations", kwargs={"edit_ID": self.product_edit.id}
            ),
        )
        self.assertFalse(
            models.PartialProductRangeSelectedOption.objects.filter(
                product_range=self.product_range,
                product_option=self.colour_product_option,
            ).exists()
        )
        partial_product_count = models.PartialProduct.objects.filter(
            product_range=self.product_range
        ).count()
        self.assertEqual(6, partial_product_count)
        self.assertNotIn(
            self.colour_product_option, self.product_edit.product_option_values.all()
        )

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse(
                "inventory:edit_variations", kwargs={"edit_ID": self.product_edit.id}
            ),
        )
        self.assertNotIn(
            self.colour_product_option, self.product_edit.product_option_values.all()
        )

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)

    def test_get_invalid_option_ID(self):
        URL = self.get_URL(product_option_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_option_ID(self):
        URL = self.get_URL(product_option_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestAddProductOptionValuesView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None, product_option_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        if product_option_ID is None:
            product_option_ID = self.colour_product_option.id
        return f"/inventory/add_product_option_values/{edit_ID}/{product_option_ID}/"

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def get_form_data(self):
        return {
            "values": [
                self.purple_product_option_value.value,
                self.magenta_product_option_value.value,
            ]
        }

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(
            response, "inventory/product_editor/add_product_option_values.html"
        )

    def test_context(self):
        edit = self.product_edit
        product_option = self.colour_product_option
        response = self.make_get_request()
        self.assertEqual(edit, response.context["edit"])
        self.assertEqual(self.product_range, response.context["product_range"])
        self.assertEqual(product_option, response.context["product_option"])
        self.assertIsInstance(
            response.context["form"], forms.AddProductOptionValuesForm
        )

    def test_post_method(self):
        edit = self.product_edit
        product_option = self.colour_product_option
        response = self.client.post(
            self.get_URL(product_option_ID=product_option.id), self.get_form_data()
        )
        self.assertRedirects(
            response,
            reverse("inventory:set_product_option_values", kwargs={"edit_ID": edit.id}),
        )
        self.assertIn(
            self.purple_product_option_value,
            self.product_edit.product_option_values.all(),
        )
        self.assertIn(
            self.magenta_product_option_value,
            self.product_edit.product_option_values.all(),
        )

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)

    def test_get_invalid_option_ID(self):
        URL = self.get_URL(product_option_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_option_ID(self):
        URL = self.get_URL(product_option_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestRemoveProductOptionValueView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None, option_value_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        if option_value_ID is None:
            option_value_ID = self.red_product_option_value.id
        return f"/inventory/remove_product_option_value/{edit_ID}/{option_value_ID}/"

    def test_get_method(self):
        edit = self.product_edit
        edit.product_option_values.add(self.purple_product_option_value)
        self.assertIn(
            self.purple_product_option_value, edit.product_option_values.all()
        )
        response = self.client.get(
            self.get_URL(option_value_ID=self.purple_product_option_value.id)
        )
        self.assertRedirects(
            response, reverse("inventory:edit_variations", kwargs={"edit_ID": edit.id})
        )
        self.assertNotIn(
            self.purple_product_option_value, edit.product_option_values.all()
        )

    def test_post_method(self):
        edit = self.product_edit
        edit.product_option_values.add(self.purple_product_option_value)
        self.assertIn(
            self.purple_product_option_value, edit.product_option_values.all()
        )
        response = self.client.post(
            self.get_URL(option_value_ID=self.purple_product_option_value.id)
        )
        self.assertRedirects(
            response, reverse("inventory:edit_variations", kwargs={"edit_ID": edit.id})
        )
        self.assertNotIn(
            self.purple_product_option_value, edit.product_option_values.all()
        )

    def test_raises_if_option_used(self):
        with self.assertRaises(Exception):
            self.client.get(
                self.get_URL(option_value_ID=self.small_product_option_value.id)
            )

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)

    def test_get_invalid_option_value_ID(self):
        URL = self.get_URL(option_value_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_option_value_ID(self):
        URL = self.get_URL(option_value_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestEditVariationView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None, product_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        if product_ID is None:
            product_ID = self.product.id
        return f"/inventory/edit_variation/{edit_ID}/{product_ID}/"

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def get_form_data(self):
        return {
            ProductEditorBase.BRAND: self.second_brand.id,
            ProductEditorBase.MANUFACTURER: self.second_manufacturer.id,
            ProductEditorBase.BARCODE: "8946516515",
            ProductEditorBase.SUPPLIER_SKU: "SC-888",
            ProductEditorBase.SUPPLIER: self.second_supplier.id,
            ProductEditorBase.PURCHASE_PRICE: 8.90,
            ProductEditorBase.VAT_RATE: self.second_VAT_rate.id,
            ProductEditorBase.PRICE: 12.50,
            ProductEditorBase.RETAIL_PRICE: 19.57,
            ProductEditorBase.LOCATION + "_0": self.warehouse_2.id,
            ProductEditorBase.LOCATION + "_1": [self.warehouse_2_bay_1.id],
            ProductEditorBase.PACKAGE_TYPE: self.second_package_type.id,
            ProductEditorBase.INTERNATIONAL_SHIPPING: self.second_international_shipping.id,
            ProductEditorBase.WEIGHT: 850,
            ProductEditorBase.DIMENSIONS + "_0": 90,
            ProductEditorBase.DIMENSIONS + "_1": 500,
            ProductEditorBase.DIMENSIONS + "_2": 124,
            ProductEditorBase.GENDER: self.second_gender.id,
        }

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(
            response, "inventory/product_editor/edit_variation.html"
        )

    def test_context(self):
        response = self.make_get_request()
        self.assertEqual(self.product_edit, response.context["edit"])
        self.assertEqual(self.product_range, response.context["product_range"])
        self.assertEqual(self.product, response.context["product"])
        self.assertIsInstance(response.context["form"], forms.ProductForm)

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse(
                "inventory:edit_variation",
                kwargs={"edit_ID": self.product_edit.id, "product_ID": self.product.id},
            ),
        )

    def test_product_edit(self):
        self.make_post_request()
        product = self.product
        self.assertEqual(self.second_brand, product.brand)
        self.assertEqual("8946516515", product.barcode)
        self.assertEqual(self.second_manufacturer, product.manufacturer)
        self.assertEqual("SC-888", product.supplier_SKU)
        self.assertEqual(self.second_supplier, product.supplier)
        self.assertEqual(Decimal("8.90"), product.purchase_price)
        self.assertEqual(self.second_VAT_rate, product.VAT_rate)
        self.assertEqual(Decimal("12.50"), product.price)
        self.assertEqual(Decimal("19.57"), product.retail_price)
        self.assertEqual([self.warehouse_2_bay_1], list(product.bays.all()))
        self.assertEqual(self.second_package_type, product.package_type)
        self.assertEqual(
            self.second_international_shipping, product.international_shipping
        )
        self.assertEqual(850, product.weight_grams)
        self.assertEqual(90, product.height_mm)
        self.assertEqual(500, product.length_mm)
        self.assertEqual(124, product.width_mm)
        self.assertEqual(self.second_gender, product.gender)

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)

    def test_get_invalid_product_ID(self):
        URL = self.get_URL(product_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_oroduct_ID(self):
        URL = self.get_URL(product_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestEditAllVariationsView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/edit_all_variations/{edit_ID}/"

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def get_form_data(self):
        form_count = len(self.variations)
        form_data = {"form-TOTAL_FORMS": form_count, "form-INITIAL_FORMS": 0}
        for i in range(form_count):
            form_data[f"form-{i}-{ProductEditorBase.BRAND}"] = self.second_brand.id
            form_data[
                f"form-{i}-{ProductEditorBase.MANUFACTURER}"
            ] = self.second_manufacturer.id
            form_data[f"form-{i}-{ProductEditorBase.BARCODE}"] = "8946516515"
            form_data[f"form-{i}-{ProductEditorBase.SUPPLIER_SKU}"] = "SC-888"
            form_data[
                f"form-{i}-{ProductEditorBase.SUPPLIER}"
            ] = self.second_supplier.id
            form_data[f"form-{i}-{ProductEditorBase.PURCHASE_PRICE}"] = 8.90
            form_data[
                f"form-{i}-{ProductEditorBase.VAT_RATE}"
            ] = self.second_VAT_rate.id
            form_data[f"form-{i}-{ProductEditorBase.PRICE}"] = 12.50
            form_data[f"form-{i}-{ProductEditorBase.RETAIL_PRICE}"] = 19.57
            form_data[f"form-{i}-{ProductEditorBase.LOCATION}_0"] = self.warehouse_2.id
            form_data[
                f"form-{i}-{ProductEditorBase.LOCATION}_1"
            ] = self.warehouse_2_bay_1.id
            form_data[
                f"form-{i}-{ProductEditorBase.PACKAGE_TYPE}"
            ] = self.second_package_type.id
            form_data[
                f"form-{i}-{ProductEditorBase.INTERNATIONAL_SHIPPING}"
            ] = self.second_international_shipping.id
            form_data[f"form-{i}-{ProductEditorBase.WEIGHT}"] = 850
            form_data[f"form-{i}-{ProductEditorBase.DIMENSIONS}_0"] = 90
            form_data[f"form-{i}-{ProductEditorBase.DIMENSIONS}_1"] = 500
            form_data[f"form-{i}-{ProductEditorBase.DIMENSIONS}_2"] = 124
            form_data[f"form-{i}-{ProductEditorBase.GENDER}"] = self.second_gender.id
        return form_data

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(
            response, "inventory/product_editor/edit_all_variations.html"
        )

    def test_context(self):
        response = self.make_get_request()
        self.assertEqual(self.product_edit, response.context["edit"])
        self.assertEqual(self.product_range, response.context["product_range"])
        self.assertIsInstance(response.context["formset"], forms.VariationsFormSet)
        self.assertEqual(
            self.product_range.variation_values(), response.context["variations"]
        )

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse("inventory:edit_product", kwargs={"edit_ID": self.product_edit.id}),
        )
        for product in self.variations:
            self.assertEqual(self.second_brand, product.brand)
            self.assertEqual("8946516515", product.barcode)
            self.assertEqual(self.second_manufacturer, product.manufacturer)
            self.assertEqual("SC-888", product.supplier_SKU)
            self.assertEqual(self.second_supplier, product.supplier)
            self.assertEqual(Decimal("8.90"), product.purchase_price)
            self.assertEqual(self.second_VAT_rate, product.VAT_rate)
            self.assertEqual(Decimal("12.50"), product.price)
            self.assertEqual(Decimal("19.57"), product.retail_price)
            self.assertEqual([self.warehouse_2_bay_1], list(product.bays.all()))
            self.assertEqual(self.second_package_type, product.package_type)
            self.assertEqual(
                self.second_international_shipping, product.international_shipping
            )
            self.assertEqual(850, product.weight_grams)
            self.assertEqual(90, product.height_mm)
            self.assertEqual(500, product.length_mm)
            self.assertEqual(124, product.width_mm)
            self.assertEqual(self.second_gender, product.gender)

    def test_invalid_form_submission(self):
        form_data = self.get_form_data()
        form_data.pop(f"form-0-{ProductEditorBase.PRICE}")
        response = self.client.post(self.get_URL(), form_data)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(
            response, "inventory/product_editor/edit_all_variations.html"
        )
        self.assertIn(ProductEditorBase.PRICE, response.context["formset"][0].errors)

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestCreateVariationView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/create_variation/{edit_ID}/"

    def get_form_data(self):
        return {
            "1": self.red_product_option_value.id,
            "2": self.small_product_option_value.id,
        }

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def test_post_method(self):
        self.small_red_product.delete()
        edit = self.product_edit
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse("inventory:edit_product", kwargs={"edit_ID": edit.id}),
            status_code=302,
            target_status_code=302,
        )
        variations = list(self.variations)
        self.assertEqual(9, len(variations))
        new_product = variations[-1]
        for option in (self.small_product_option_value, self.red_product_option_value):
            self.assertTrue(
                models.PartialProductOptionValueLink.objects.filter(
                    product=new_product, product_option_value=option
                ).exists()
            )

    def test_get_method(self):
        self.small_red_product.delete()
        edit = self.product_edit
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse("inventory:edit_product", kwargs={"edit_ID": edit.id}),
            status_code=302,
            target_status_code=302,
        )

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestDeleteVariationView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None, product_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        if product_ID is None:
            product_ID = self.product.id
        return f"/inventory/delete_variation/{edit_ID}/{product_ID}/"

    def test_get_method(self):
        edit = self.product_edit
        product = self.product
        product.pre_existing = False
        product.save()
        response = self.make_get_request()
        self.assertRedirects(
            response, reverse("inventory:edit_product", kwargs={"edit_ID": edit.id})
        )
        self.assertFalse(models.PartialProduct.objects.filter(id=product.id).exists())

    def test_post_method(self):
        edit = self.product_edit
        product = self.product
        product.pre_existing = False
        product.save()
        response = self.make_post_request()
        self.assertRedirects(
            response, reverse("inventory:edit_product", kwargs={"edit_ID": edit.id})
        )
        self.assertFalse(models.PartialProduct.objects.filter(id=product.id).exists())

    def test_pre_existing_product_not_deleted(self):
        edit = self.product_edit
        product = self.product
        response = self.make_get_request()
        self.assertRedirects(
            response, reverse("inventory:edit_product", kwargs={"edit_ID": edit.id})
        )
        self.assertTrue(models.PartialProduct.objects.filter(id=product.id).exists())

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)

    def test_get_invalid_product_ID(self):
        URL = self.get_URL(product_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_oroduct_ID(self):
        URL = self.get_URL(product_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestDiscardChangesView(
    InventoryViewTest, fixtures.EditingProductFixture, ViewTests
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/discard_changes/{edit_ID}/"

    def test_get_method(self):
        edit = self.product_edit
        product_range = edit.partial_product_range
        original_range = edit.product_range
        response = self.make_get_request()
        self.assertRedirects(
            response,
            reverse(
                "inventory:product_range", kwargs={"range_id": original_range.range_ID}
            ),
        )
        self.assertFalse(
            models.PartialProductRangeSelectedOption.objects.filter(
                id=product_range.id
            ).exists()
        )
        self.assertFalse(models.ProductEdit.objects.filter(id=edit.id).exists())

    def test_post_method(self):
        edit = self.product_edit
        product_range = edit.partial_product_range
        original_range = edit.product_range
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse(
                "inventory:product_range", kwargs={"range_id": original_range.range_ID}
            ),
        )
        self.assertFalse(
            models.PartialProductRangeSelectedOption.objects.filter(
                id=product_range.id
            ).exists()
        )
        self.assertFalse(models.ProductEdit.objects.filter(id=edit.id).exists())

    def test_redirect_for_new_range(self):
        edit = self.product_edit
        product_range = edit.partial_product_range
        edit.product_range = None
        edit.save()
        response = self.make_get_request()
        self.assertRedirects(response, reverse("inventory:product_search"))
        self.assertFalse(
            models.PartialProductRangeSelectedOption.objects.filter(
                id=product_range.id
            ).exists()
        )
        self.assertFalse(models.ProductEdit.objects.filter(id=edit.id).exists())

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)


class TestSaveChangesView(InventoryViewTest, fixtures.EditingProductFixture, ViewTests):
    fixtures = fixtures.EditingProductFixture.fixtures

    def get_URL(self, edit_ID=None):
        if edit_ID is None:
            edit_ID = self.product_edit.id
        return f"/inventory/save_changes/{edit_ID}/"

    @patch("inventory.views.product_editor.SaveEdit")
    def test_get_method(self, mock_SaveEdit):
        mock_save_edit = Mock()
        mock_SaveEdit.return_value = mock_save_edit
        edit = self.product_edit
        original_range = edit.product_range
        response = self.make_get_request()
        self.assertRedirects(
            response,
            reverse(
                "inventory:product_range", kwargs={"range_id": original_range.range_ID}
            ),
        )
        mock_SaveEdit.assert_called_once_with(edit, self.user)
        mock_save_edit.save_edit_threaded.assert_called_once()

    @patch("inventory.views.product_editor.SaveEdit")
    def test_post_method(self, mock_SaveEdit):
        mock_save_edit = Mock()
        mock_SaveEdit.return_value = mock_save_edit
        edit = self.product_edit
        original_range = edit.product_range
        response = self.make_post_request()
        self.assertRedirects(
            response,
            reverse(
                "inventory:product_range", kwargs={"range_id": original_range.range_ID}
            ),
        )
        mock_SaveEdit.assert_called_once_with(edit, self.user)
        mock_save_edit.save_edit_threaded.assert_called_once()

    @patch("inventory.views.product_editor.SaveEdit")
    def test_post_method_with_new_range(self, mock_SaveEdit):
        mock_save_edit = Mock()
        mock_SaveEdit.return_value = mock_save_edit
        edit = self.product_edit
        edit.product_range = None
        edit.save()
        response = self.make_post_request()
        self.assertRedirects(response, reverse("inventory:continue"))
        mock_SaveEdit.assert_called_once_with(edit, self.user)
        mock_save_edit.save_edit_threaded.assert_called_once()

    def test_get_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.get(URL)
        self.assertEqual(404, response.status_code)

    def test_post_invalid_edit_ID(self):
        URL = self.get_URL(edit_ID="99999")
        response = self.client.post(URL)
        self.assertEqual(404, response.status_code)
