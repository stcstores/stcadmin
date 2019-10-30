import json
from unittest.mock import Mock, patch

from inventory import forms, models
from inventory.tests import fixtures
from product_editor.editor_manager import ProductEditorBase

from .form_test import FormTest


class TestDescriptionForm(FormTest):
    TITLE = "title"
    DEPARTMENT = "department"
    DESCRIPTION = "description"
    AMAZON_BULLETS = "amazon_bullets"
    SEARCH_TERMS = "search_terms"

    TITLE_VALUE = "Test Title"
    DESCRIPTION_VALUE = "A description.\nOf a product."
    AMAZON_BULLETS_VALUE = ["One", "Two", "Three"]
    SEARCH_TERMS_VALUE = ["Four", "Five", "Six"]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.department = models.Department.objects.create(
            name="Test Department", product_option_value_ID="28493"
        )
        cls.department_value = cls.department.id

    def test_form_valid(self):
        form_data = {
            self.TITLE: self.TITLE_VALUE,
            self.DEPARTMENT: self.department_value,
            self.DESCRIPTION: self.DESCRIPTION_VALUE,
            self.AMAZON_BULLETS: json.dumps(self.AMAZON_BULLETS_VALUE),
            self.SEARCH_TERMS: json.dumps(self.SEARCH_TERMS_VALUE),
        }
        form = forms.DescriptionForm(form_data)
        self.assert_form_is_valid(form)
        self.assertEqual(form.cleaned_data[self.TITLE], self.TITLE_VALUE)
        self.assertEqual(form.cleaned_data[self.DEPARTMENT], self.department)
        self.assertEqual(form.cleaned_data[self.DESCRIPTION], self.DESCRIPTION_VALUE)
        self.assertEqual(
            form.cleaned_data[self.AMAZON_BULLETS], self.AMAZON_BULLETS_VALUE
        )
        self.assertEqual(form.cleaned_data[self.SEARCH_TERMS], self.SEARCH_TERMS_VALUE)

    def test_form_without_title(self):
        form_data = {
            self.DEPARTMENT: self.department_value,
            self.DESCRIPTION: self.DESCRIPTION_VALUE,
            self.AMAZON_BULLETS: json.dumps(self.AMAZON_BULLETS_VALUE),
            self.SEARCH_TERMS: json.dumps(self.SEARCH_TERMS_VALUE),
        }
        form = forms.DescriptionForm(form_data)
        self.assert_form_invalid(form)
        self.assertIn(self.TITLE, form.errors)

    def test_form_without_department(self):
        form_data = {
            self.TITLE: self.TITLE_VALUE,
            self.DESCRIPTION: self.DESCRIPTION_VALUE,
            self.AMAZON_BULLETS: json.dumps(self.AMAZON_BULLETS_VALUE),
            self.SEARCH_TERMS: json.dumps(self.SEARCH_TERMS_VALUE),
        }
        form = forms.DescriptionForm(form_data)
        self.assert_form_invalid(form)
        self.assertIn(self.DEPARTMENT, form.errors)

    def test_form_without_description(self):
        form_data = {
            self.TITLE: self.TITLE_VALUE,
            self.DEPARTMENT: self.department_value,
            self.AMAZON_BULLETS: json.dumps(self.AMAZON_BULLETS_VALUE),
            self.SEARCH_TERMS: json.dumps(self.SEARCH_TERMS_VALUE),
        }
        form = forms.DescriptionForm(form_data)
        self.assert_form_is_valid(form)
        self.assertEqual(form.cleaned_data[self.DESCRIPTION], "")

    def test_form_without_amazon_bullets(self):
        form_data = {
            self.TITLE: self.TITLE_VALUE,
            self.DEPARTMENT: self.department_value,
            self.DESCRIPTION: self.DESCRIPTION_VALUE,
            self.SEARCH_TERMS: json.dumps(self.SEARCH_TERMS_VALUE),
        }
        form = forms.DescriptionForm(form_data)
        self.assert_form_is_valid(form)
        self.assertEqual(form.cleaned_data[self.AMAZON_BULLETS], [])

    def test_form_with_too_many_amazon_bullets(self):
        form_data = {
            self.TITLE: self.TITLE_VALUE,
            self.DEPARTMENT: self.department_value,
            self.DESCRIPTION: self.DESCRIPTION_VALUE,
            self.AMAZON_BULLETS: json.dumps(
                ["One", "Two", "Three", "Four", "Five", "Six"]
            ),
            self.SEARCH_TERMS: json.dumps(self.SEARCH_TERMS_VALUE),
        }
        form = forms.DescriptionForm(form_data)
        self.assert_form_invalid(form)

    def test_form_without_search_terms(self):
        form_data = {
            self.TITLE: self.TITLE_VALUE,
            self.DEPARTMENT: self.department_value,
            self.DESCRIPTION: self.DESCRIPTION_VALUE,
            self.AMAZON_BULLETS: json.dumps(self.AMAZON_BULLETS_VALUE),
        }
        form = forms.DescriptionForm(form_data)
        self.assert_form_is_valid(form)
        self.assertEqual(form.cleaned_data[self.SEARCH_TERMS], [])

    def test_form_with_too_many_search_terms(self):
        form_data = {
            self.TITLE: self.TITLE_VALUE,
            self.DEPARTMENT: self.department_value,
            self.DESCRIPTION: self.DESCRIPTION_VALUE,
            self.AMAZON_BULLETS: json.dumps(self.AMAZON_BULLETS_VALUE),
            self.SEARCH_TERMS: json.dumps(
                ["One", "Two", "Three", "Four", "Five", "Six"]
            ),
        }
        form = forms.DescriptionForm(form_data)
        self.assert_form_invalid(form)


class TestCreateBayForm(FormTest, fixtures.ProductRequirementsFixture):
    fixtures = fixtures.ProductRequirementsFixture.fixtures

    DEPARTMENT = "department"
    LOCATION = "location"
    WAREHOUSE = "warehouse"
    NAME = "name"
    BAY_TYPE = "bay_type"

    name_value = "New Bay"

    def test_primary_bay_valid(self):
        form_data = {
            self.DEPARTMENT: self.department.id,
            self.NAME: self.name_value,
            self.BAY_TYPE: forms.CreateBayForm.PRIMARY,
        }
        form = forms.CreateBayForm(form_data)
        self.assert_form_is_valid(form)
        self.assertEqual(form.cleaned_data[self.DEPARTMENT], self.department)
        self.assertEqual(form.cleaned_data[self.WAREHOUSE], self.warehouse_1)
        self.assertEqual(form.cleaned_data[self.NAME], self.name_value)
        self.assertEqual(form.cleaned_data[self.BAY_TYPE], forms.CreateBayForm.PRIMARY)
        self.assertEqual(form.new_bay.name, self.name_value)
        self.assertEqual(form.new_bay.warehouse, self.warehouse_1)
        self.assertIsNone(form.new_bay.id)

    def test_backup_bay_valid(self):
        form_data = {
            self.LOCATION: self.warehouse_1.id,
            self.DEPARTMENT: self.department.id,
            self.NAME: self.name_value,
            self.BAY_TYPE: forms.CreateBayForm.BACKUP,
        }
        form = forms.CreateBayForm(form_data)
        self.assert_form_is_valid(form)
        self.assertEqual(form.cleaned_data[self.DEPARTMENT], self.department)
        self.assertEqual(form.cleaned_data[self.WAREHOUSE], self.warehouse_1)
        self.assertEqual(form.cleaned_data[self.NAME], self.name_value)
        self.assertEqual(form.cleaned_data[self.BAY_TYPE], forms.CreateBayForm.BACKUP)
        expected_name = (
            f"{self.warehouse_1.abriviation} Backup "
            f"{self.department.name} {self.name_value}"
        )
        self.assertEqual(form.new_bay.name, expected_name)
        self.assertEqual(form.new_bay.warehouse, self.warehouse_1)
        self.assertIsNone(form.new_bay.id)

    def test_raises_for_backup_without_location(self):
        form_data = {
            self.DEPARTMENT: self.department.id,
            self.NAME: self.name_value,
            self.BAY_TYPE: forms.CreateBayForm.BACKUP,
        }
        form = forms.CreateBayForm(form_data)
        self.assert_form_invalid(form)

    @patch("inventory.models.locations.CCAPI")
    def test_save_method(self, mock_CCAPI):
        new_bay_ID = "979461"
        mock_CCAPI.get_bay_id.return_value = new_bay_ID
        form_data = {
            self.DEPARTMENT: self.department.id,
            self.NAME: self.name_value,
            self.BAY_TYPE: forms.CreateBayForm.PRIMARY,
        }
        form = forms.CreateBayForm(form_data)
        self.assert_form_is_valid(form)
        self.assertIsNone(form.new_bay.id)
        form.save()
        mock_CCAPI.get_bay_id.assert_called_once_with(
            self.name_value, self.warehouse_1.name, create=True
        )
        self.assertIsNotNone(form.new_bay.id)
        self.assertEqual(form.new_bay.bay_ID, new_bay_ID)


class TestProductForm(fixtures.VariationProductRangeFixture, FormTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.warehouse = models.Warehouse.objects.create(
            name="Warehouse", abriviation="WH", warehouse_ID="93943"
        )
        cls.bays = [
            models.Bay.objects.create(
                name="New Bay",
                bay_ID="383492",
                warehouse=cls.warehouse,
                is_default=False,
            )
        ]

    def setUp(self):
        self.product.bays.set([self.bays[0]])
        self.form_data = {
            ProductEditorBase.BRAND: self.brand.id,
            ProductEditorBase.MANUFACTURER: self.manufacturer.id,
            ProductEditorBase.BARCODE: self.product.barcode,
            ProductEditorBase.SUPPLIER_SKU: self.product.supplier_SKU,
            ProductEditorBase.SUPPLIER: self.supplier.id,
            ProductEditorBase.PURCHASE_PRICE: self.product.purchase_price,
            ProductEditorBase.VAT_RATE: self.VAT_rate.id,
            ProductEditorBase.PRICE: self.product.price,
            ProductEditorBase.RETAIL_PRICE: self.product.retail_price,
            ProductEditorBase.LOCATION + "_0": self.warehouse.id,
            ProductEditorBase.LOCATION + "_1": [self.bays[0].id],
            ProductEditorBase.PACKAGE_TYPE: self.package_type.id,
            ProductEditorBase.INTERNATIONAL_SHIPPING: self.international_shipping.id,
            ProductEditorBase.WEIGHT: self.product.weight_grams,
            ProductEditorBase.DIMENSIONS + "_0": self.product.height_mm,
            ProductEditorBase.DIMENSIONS + "_1": self.product.length_mm,
            ProductEditorBase.DIMENSIONS + "_2": self.product.width_mm,
            ProductEditorBase.GENDER: self.gender.id,
        }

    def get_form(self, *args, **kwargs):
        return forms.ProductForm(*args, **kwargs)

    def test_product_form(self):
        form = self.get_form(self.form_data, product=self.product, user=self.user)
        self.assert_form_is_valid(form)
        self.assertEqual(form.cleaned_data[ProductEditorBase.BRAND], self.brand)
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.MANUFACTURER], self.manufacturer
        )
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.BARCODE], self.product.barcode
        )
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.SUPPLIER_SKU], self.product.supplier_SKU
        )
        self.assertEqual(form.cleaned_data[ProductEditorBase.SUPPLIER], self.supplier)
        self.assertEqual(
            round(float(form.cleaned_data[ProductEditorBase.PURCHASE_PRICE]), 2),
            round(float(self.product.purchase_price), 2),
        )
        self.assertEqual(form.cleaned_data[ProductEditorBase.VAT_RATE], self.VAT_rate)
        self.assertEqual(
            round(float(form.cleaned_data[ProductEditorBase.PRICE]), 2),
            round(float(self.product.price), 2),
        )
        self.assertEqual(
            round(float(form.cleaned_data[ProductEditorBase.RETAIL_PRICE]), 2),
            round(float(self.product.retail_price), 2),
        )
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.LOCATION][ProductEditorBase.WAREHOUSE],
            self.warehouse,
        )
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.LOCATION][ProductEditorBase.BAYS],
            [self.bays[0]],
        )
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.PACKAGE_TYPE], self.package_type
        )
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.INTERNATIONAL_SHIPPING],
            self.international_shipping,
        )
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.WEIGHT], self.product.weight_grams
        )
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.DIMENSIONS][ProductEditorBase.HEIGHT],
            self.product.height_mm,
        )
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.DIMENSIONS][ProductEditorBase.LENGTH],
            self.product.length_mm,
        )
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.DIMENSIONS][ProductEditorBase.WIDTH],
            self.product.width_mm,
        )

        self.assertEqual(form.cleaned_data[ProductEditorBase.GENDER], self.gender)

    def test_product_form_without_brand(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.BRAND)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_manufacturer(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.MANUFACTURER)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_barcode(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.BARCODE)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_price(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.PRICE)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_VAT_rate(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.VAT_RATE)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_warehouse(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.LOCATION + "_0")
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_bays(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.LOCATION + "_1")
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_weight(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.WEIGHT)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_is_valid(form)
        self.assertEqual(form.cleaned_data[ProductEditorBase.WEIGHT], 0)

    def test_product_form_without_purchase_price(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.PURCHASE_PRICE)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_retail_price(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.RETAIL_PRICE)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_package_type(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.PACKAGE_TYPE)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_supplier(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.SUPPLIER)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_supplier_SKU(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.SUPPLIER_SKU)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_is_valid(form)
        self.assertEqual(form.cleaned_data[ProductEditorBase.SUPPLIER_SKU], "")

    def test_product_form_without_international_shipping(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.INTERNATIONAL_SHIPPING)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_invalid(form)

    def test_product_form_without_gender(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.GENDER)
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_is_valid(form)
        self.assertIsNone(form.cleaned_data[ProductEditorBase.GENDER])

    def test_product_form_without_height(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.DIMENSIONS + "_0")
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_is_valid(form)
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.DIMENSIONS][ProductEditorBase.HEIGHT], 0
        )

    def test_product_form_without_length(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.DIMENSIONS + "_1")
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_is_valid(form)
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.DIMENSIONS][ProductEditorBase.LENGTH], 0
        )

    def test_product_form_without_width(self):
        data = dict(self.form_data)
        data.pop(ProductEditorBase.DIMENSIONS + "_2")
        form = self.get_form(data, product=self.product, user=self.user)
        self.assert_form_is_valid(form)
        self.assertEqual(
            form.cleaned_data[ProductEditorBase.DIMENSIONS][ProductEditorBase.WIDTH], 0
        )

    def test_with_product_with_no_bays(self):
        self.product.bays.set([])
        form = self.get_form(product=self.product, user=self.user)
        initial = form.get_initial()
        self.assertNotIn(ProductEditorBase.LOCATION, initial)

    def test_initial(self):
        form = self.get_form(product=self.product, user=self.user)
        initial = form.get_initial()
        self.assertEqual(initial[ProductEditorBase.BRAND], self.product.brand)
        self.assertEqual(
            initial[ProductEditorBase.MANUFACTURER], self.product.manufacturer
        )
        self.assertEqual(initial[ProductEditorBase.BARCODE], self.product.barcode)
        self.assertEqual(initial[ProductEditorBase.PRICE], self.product.price)
        self.assertEqual(initial[ProductEditorBase.VAT_RATE], self.product.VAT_rate)
        self.assertEqual(
            initial[ProductEditorBase.LOCATION][ProductEditorBase.WAREHOUSE],
            self.warehouse.id,
        )
        self.assertEqual(
            initial[ProductEditorBase.LOCATION][ProductEditorBase.BAYS],
            [self.bays[0].id],
        )
        self.assertEqual(
            initial[ProductEditorBase.DIMENSIONS][ProductEditorBase.HEIGHT],
            self.product.height_mm,
        )
        self.assertEqual(
            initial[ProductEditorBase.DIMENSIONS][ProductEditorBase.LENGTH],
            self.product.length_mm,
        )
        self.assertEqual(
            initial[ProductEditorBase.DIMENSIONS][ProductEditorBase.WIDTH],
            self.product.width_mm,
        )
        self.assertEqual(initial[ProductEditorBase.WEIGHT], self.product.weight_grams)
        self.assertEqual(
            initial[ProductEditorBase.PURCHASE_PRICE], self.product.purchase_price
        )
        self.assertEqual(
            initial[ProductEditorBase.RETAIL_PRICE], self.product.retail_price
        )
        self.assertEqual(
            initial[ProductEditorBase.PACKAGE_TYPE], self.product.package_type
        )
        self.assertEqual(initial[ProductEditorBase.SUPPLIER], self.product.supplier)
        self.assertEqual(
            initial[ProductEditorBase.SUPPLIER_SKU], self.product.supplier_SKU
        )
        self.assertEqual(
            initial[ProductEditorBase.INTERNATIONAL_SHIPPING],
            self.product.international_shipping,
        )
        self.assertEqual(initial[ProductEditorBase.GENDER], self.product.gender)

    def test_error_is_added_for_product_with_mixed_warehouses(self):
        self.product.bays.set((self.warehouse_1_bay_1, self.warehouse_2_bay_1))
        with self.assertRaises(ValueError):
            self.get_form(product=self.product, user=self.user)

    def test_save_method(self):
        updater_class = Mock()
        updater = Mock()
        updater_class.return_value = updater
        form = self.get_form(self.form_data, product=self.product, user=self.user)
        self.assert_form_is_valid(form)
        form.save(updater_class=updater_class)
        updater_class.assert_called_once_with(self.product, self.user)
        updater.set_brand.assert_called_once_with(self.product.brand)
        updater.set_manufacturer.assert_called_once_with(self.product.manufacturer)
        updater.set_barcode.assert_called_once_with(self.product.barcode)
        updater.set_price.assert_called_once_with(self.product.price)
        updater.set_VAT_rate.assert_called_once_with(self.product.VAT_rate)
        updater.set_bays.assert_called_once_with([self.bays[0]])
        updater.set_width.assert_called_once_with(self.product.width_mm)
        updater.set_height.assert_called_once_with(self.product.height_mm)
        updater.set_length.assert_called_once_with(self.product.length_mm)
        updater.set_weight.assert_called_once_with(self.product.weight_grams)
        updater.set_package_type.assert_called_once_with(self.product.package_type)
        updater.set_international_shipping.assert_called_once_with(
            self.product.international_shipping
        )
        updater.set_purchase_price.assert_called_once_with(self.product.purchase_price)
        updater.set_retail_price.assert_called_once_with(self.product.retail_price)
        updater.set_supplier.assert_called_once_with(self.product.supplier)
        updater.set_supplier_SKU.assert_called_once_with(self.product.supplier_SKU)
        updater.set_gender.assert_called_once_with(self.product.gender)


class TestVariationForm(TestProductForm):
    def get_form(self, *args, **kwargs):
        return forms.VariationForm(*args, **kwargs)


class TestAddProductOptionForm(fixtures.EditingProductFixture, FormTest):
    def test_form(self):
        data = {
            "option": self.design_product_option.id,
            f"values_{self.design_product_option.id}": [
                self.cat_product_option_value.value,
                self.dog_product_option_value.value,
                self.horse_product_option_value.value,
            ],
        }
        form = forms.AddProductOption(
            data, edit=self.product_edit, variation=True, user=self.user
        )
        self.assert_form_is_valid(form)
        self.assertEqual(form.cleaned_data["option"], self.design_product_option)
        self.assertEqual(
            form.cleaned_data[f"values_{self.design_product_option.id}"],
            [
                self.cat_product_option_value,
                self.dog_product_option_value,
                self.horse_product_option_value,
            ],
        )

    def test_not_enough_values(self):
        data = {
            "option": self.design_product_option.id,
            f"values_{self.design_product_option.id}": [
                self.cat_product_option_value.value
            ],
        }
        form = forms.AddProductOption(
            data, edit=self.product_edit, variation=True, user=self.user
        )
        self.assert_form_invalid(form)
        self.assertIn(f"values_{self.design_product_option.id}", form.errors)

    def test_no_values(self):
        data = {
            "option": self.design_product_option.id,
            f"values_{self.design_product_option.id}": [],
        }
        form = forms.AddProductOption(
            data, edit=self.product_edit, variation=True, user=self.user
        )
        self.assert_form_invalid(form)
        self.assertIn(f"values_{self.design_product_option.id}", form.errors)

    def save_method_test(self, variation):
        form = forms.AddProductOption(
            {}, edit=self.product_edit, variation=True, user=self.user
        )
        self.assert_form_invalid(form)

        data = {
            "option": self.design_product_option.id,
            f"values_{self.design_product_option.id}": [
                self.cat_product_option_value.value,
                self.dog_product_option_value.value,
                self.horse_product_option_value.value,
            ],
        }
        form = forms.AddProductOption(
            data, edit=self.product_edit, variation=variation, user=self.user
        )
        self.assert_form_is_valid(form)
        form.save()
        self.assertTrue(
            models.PartialProductRangeSelectedOption.objects.filter(
                product_range=self.product_range,
                product_option=self.design_product_option,
                variation=variation,
                pre_existing=False,
            ).exists()
        )
        values = (
            self.cat_product_option_value,
            self.dog_product_option_value,
            self.horse_product_option_value,
        )
        for value in values:
            self.assertIn(value, self.product_edit.product_option_values.all())

    def test_save_method_for_variation(self):
        self.save_method_test(True)

    def test_save_method_for_non_variation(self):
        self.save_method_test(False)


class TestSetProductOptionValuesForm(fixtures.EditingProductFixture, FormTest):
    def test_form(self):
        form = forms.SetProductOptionValues(
            edit=self.product_edit,
            product_range=self.product_range,
            product=self.product,
        )
        self.assertQuerysetEqual(
            form.variation_options, map(repr, self.product_range.variation_options())
        )
        self.assertQuerysetEqual(
            form.listing_options, map(repr, self.product_range.listing_options())
        )
        for option in self.product_range.product_options.all():
            self.assertIn(f"option_{option.name}", form.fields)

    def test_initial(self):
        form = forms.SetProductOptionValues(
            edit=self.product_edit,
            product_range=self.product_range,
            product=self.product,
        )
        initial = form.get_initial()
        self.assertDictEqual(
            {
                "product_ID": self.product.id,
                "option_Colour": self.red_product_option_value,
                "option_Size": self.small_product_option_value,
                "option_Model": self.model_product_option_value,
            },
            initial,
        )

    def test_initial_for_no_options_set(self):
        models.PartialProductOptionValueLink.objects.filter(
            product=self.product
        ).delete()
        self.product_range.product_options.set(
            (self.colour_product_option, self.size_product_option)
        )
        form = forms.SetProductOptionValues(
            edit=self.product_edit,
            product_range=self.product_range,
            product=self.product,
        )
        initial = form.get_initial()
        self.assertDictEqual({"product_ID": self.product.id}, initial)

    def test_initial_sets_listing_option_only_available_value(self):
        models.PartialProductOptionValueLink.objects.filter(
            product=self.product
        ).delete()
        form = forms.SetProductOptionValues(
            edit=self.product_edit,
            product_range=self.product_range,
            product=self.product,
        )
        initial = form.get_initial()
        self.assertDictEqual(
            {
                "product_ID": self.product.id,
                "option_Model": self.model_product_option_value,
            },
            initial,
        )

    def test_initial_listing_option_not_set_when_multiple_available(self):
        models.PartialProductOptionValueLink.objects.filter(
            product=self.product
        ).delete()
        second_model_product_option_value = models.ProductOptionValue.objects.create(
            value="Model B293",
            product_option=self.model_product_option,
            product_option_value_ID="843995",
        )
        self.product_edit.product_option_values.add(second_model_product_option_value)
        form = forms.SetProductOptionValues(
            edit=self.product_edit,
            product_range=self.product_range,
            product=self.product,
        )
        initial = form.get_initial()
        self.assertDictEqual({"product_ID": self.product.id}, initial)

    def test_pre_existing_field_is_disabled(self):
        option = models.PartialProductRangeSelectedOption.objects.get(
            product_range=self.product_range, product_option=self.colour_product_option
        )
        option.pre_existing = False
        option.save()
        form = forms.SetProductOptionValues(
            edit=self.product_edit,
            product_range=self.product_range,
            product=self.product,
        )
        self.assertTrue(
            form.fields[f"option_{self.size_product_option.name}"].widget.attrs[
                "disabled"
            ]
        )
        self.assertNotIn(
            "disabled",
            form.fields[f"option_{self.colour_product_option.name}"].widget.attrs,
        )
        self.assertNotIn(
            "disabled",
            form.fields[f"option_{self.model_product_option.name}"].widget.attrs,
        )

    def test_form_data(self):
        data = {
            "product_ID": self.product.product_ID,
            f"option_{self.colour_product_option.name}": self.blue_product_option_value.id,
            f"option_{self.size_product_option.name}": self.large_product_option_value.id,
            f"option_{self.model_product_option.name}": self.model_product_option_value.id,
        }
        form = forms.SetProductOptionValues(
            data,
            edit=self.product_edit,
            product_range=self.product_range,
            product=self.product,
        )
        self.assert_form_is_valid(form)
        self.assertDictEqual(
            {
                "product_ID": self.product.product_ID,
                f"option_{self.colour_product_option.name}": self.blue_product_option_value,
                f"option_{self.size_product_option.name}": self.large_product_option_value,
                f"option_{self.model_product_option.name}": self.model_product_option_value,
            },
            form.cleaned_data,
        )

    def test_empty_product_option_value(self):
        data = {
            "product_ID": self.product.product_ID,
            f"option_{self.colour_product_option.name}": self.blue_product_option_value.id,
            f"option_{self.size_product_option.name}": self.large_product_option_value.id,
        }
        form = forms.SetProductOptionValues(
            data,
            edit=self.product_edit,
            product_range=self.product_range,
            product=self.product,
        )
        self.assert_form_invalid(form)
        self.assertIn(f"option_{self.model_product_option}", form.errors)

    def test_variation(self):
        data = {
            "product_ID": self.product.id,
            f"option_{self.colour_product_option.name}": self.blue_product_option_value.id,
            f"option_{self.size_product_option.name}": self.large_product_option_value.id,
            f"option_{self.model_product_option.name}": self.model_product_option_value.id,
        }
        form = forms.SetProductOptionValues(
            data,
            edit=self.product_edit,
            product_range=self.product_range,
            product=self.product,
        )
        self.assert_form_is_valid(form)
        self.assertDictEqual(
            {
                f"option_{self.colour_product_option.name}": self.blue_product_option_value,
                f"option_{self.size_product_option.name}": self.large_product_option_value,
            },
            form.variation(),
        )


class TestSetProductOptionValuesFormset(fixtures.EditingProductFixture, FormTest):
    def setUp(self):
        super().setUp()
        self.kwargs = [
            {
                "product": _,
                "edit": self.product_edit,
                "product_range": self.product_range,
            }
            for _ in self.product_range.products()
        ]

    def get_form_data(self):
        data = {"form-TOTAL_FORMS": len(self.variations), "form-INITIAL_FORMS": 0}
        formset = forms.SetProductOptionValuesFormset(form_kwargs=self.kwargs)
        for i, form in enumerate(formset):
            initial = form.get_initial()
            data[f"form-{i}-product_ID"] = initial["product_ID"]
            data[f"form-{i}-option_Colour"] = initial["option_Colour"].id
            data[f"form-{i}-option_Size"] = initial["option_Size"].id
            data[f"form-{i}-option_Model"] = initial["option_Model"].id
        return data

    def test_formset(self):
        formset = forms.SetProductOptionValuesFormset(form_kwargs=self.kwargs)
        self.assertEqual(len(self.variations), len(formset))

    def test_initial(self):
        formset = forms.SetProductOptionValuesFormset(form_kwargs=self.kwargs)
        for form in formset:
            initial = form.get_initial()
            self.assertIn("product_ID", initial)
            self.assertEqual(form.product.id, initial["product_ID"])

    def test_data(self):
        formset = forms.SetProductOptionValuesFormset(
            self.get_form_data(), form_kwargs=self.kwargs
        )
        self.assert_form_is_valid(formset)
        variations = self.variations
        self.assertCountEqual(
            [
                {
                    "product_ID": str(variations[0].id),
                    "option_Size": self.small_product_option_value,
                    "option_Colour": self.red_product_option_value,
                    "option_Model": self.model_product_option_value,
                },
                {
                    "product_ID": str(variations[1].id),
                    "option_Size": self.small_product_option_value,
                    "option_Colour": self.green_product_option_value,
                    "option_Model": self.model_product_option_value,
                },
                {
                    "product_ID": str(variations[2].id),
                    "option_Size": self.small_product_option_value,
                    "option_Colour": self.blue_product_option_value,
                    "option_Model": self.model_product_option_value,
                },
                {
                    "product_ID": str(variations[3].id),
                    "option_Size": self.medium_product_option_value,
                    "option_Colour": self.red_product_option_value,
                    "option_Model": self.model_product_option_value,
                },
                {
                    "product_ID": str(variations[4].id),
                    "option_Size": self.medium_product_option_value,
                    "option_Colour": self.green_product_option_value,
                    "option_Model": self.model_product_option_value,
                },
                {
                    "product_ID": str(variations[5].id),
                    "option_Size": self.medium_product_option_value,
                    "option_Colour": self.blue_product_option_value,
                    "option_Model": self.model_product_option_value,
                },
                {
                    "product_ID": str(variations[6].id),
                    "option_Size": self.large_product_option_value,
                    "option_Colour": self.red_product_option_value,
                    "option_Model": self.model_product_option_value,
                },
                {
                    "product_ID": str(variations[7].id),
                    "option_Size": self.large_product_option_value,
                    "option_Colour": self.green_product_option_value,
                    "option_Model": self.model_product_option_value,
                },
                {
                    "product_ID": str(variations[8].id),
                    "option_Size": self.large_product_option_value,
                    "option_Colour": self.blue_product_option_value,
                    "option_Model": self.model_product_option_value,
                },
            ],
            formset.cleaned_data,
        )

    def test_non_unique_variations_are_invalid(self):
        data = self.get_form_data()
        data["form-0-option_Colour"] = self.red_product_option_value.id
        data["form-1-option_Colour"] = self.red_product_option_value.id
        data["form-0-option_Size"] = self.small_product_option_value.id
        data["form-1-option_Size"] = self.small_product_option_value.id
        formset = forms.SetProductOptionValuesFormset(data, form_kwargs=self.kwargs)
        self.assert_form_invalid(formset)
        for i, form_errors in enumerate(formset.errors):
            if i in (0, 1):
                self.assertIn(
                    "This variation is not unique within the Product Range.",
                    form_errors["__all__"],
                )
            else:
                self.assertEqual({}, form_errors)

    def test_all_the_same_listing_variation_is_invalid(self):
        data = self.get_form_data()
        for i in range(len(self.variations)):
            data[f"form-{i}-option_Colour"] = self.red_product_option_value.id
        formset = forms.SetProductOptionValuesFormset(data, form_kwargs=self.kwargs)
        self.assert_form_invalid(formset)
        for form_errors in formset.errors:
            self.assertEqual(
                [
                    (
                        "Every variation cannot have the same value for a"
                        " drop down. Should this be a listing option?"
                    )
                ],
                form_errors["option_Colour"],
            )

    def test_save_method(self):
        data = self.get_form_data()
        models.PartialProductOptionValueLink.objects.all().delete()
        self.assertEqual(0, models.PartialProductOptionValueLink.objects.all().count())
        formset = forms.SetProductOptionValuesFormset(data, form_kwargs=self.kwargs)
        self.assert_form_is_valid(formset)
        formset.save()
        self.assertEqual(27, models.PartialProductOptionValueLink.objects.all().count())
        self.assertTrue(
            models.PartialProductOptionValueLink.objects.filter(
                product=self.product, product_option_value=self.red_product_option_value
            ).exists()
        )
        self.assertTrue(
            models.PartialProductOptionValueLink.objects.filter(
                product=self.product,
                product_option_value=self.small_product_option_value,
            ).exists()
        )
        self.assertTrue(
            models.PartialProductOptionValueLink.objects.filter(
                product=self.product,
                product_option_value=self.model_product_option_value,
            ).exists()
        )


class TestAddProductOptionValuesForm(fixtures.EditingProductFixture, FormTest):
    def test_form(self):
        data = {"values": [self.red_product_option_value.value]}
        form = forms.AddProductOptionValuesForm(
            data, edit=self.product_edit, product_option=self.colour_product_option
        )
        self.assert_form_is_valid(form)
        self.assertDictEqual(
            form.cleaned_data, {"values": [self.red_product_option_value]}
        )

    def test_multiple_inputs(self):
        data = {
            "values": [
                self.red_product_option_value.value,
                self.green_product_option_value.value,
                self.blue_product_option_value.value,
            ]
        }
        form = forms.AddProductOptionValuesForm(
            data, edit=self.product_edit, product_option=self.colour_product_option
        )
        self.assert_form_is_valid(form)
        self.assertDictEqual(
            {
                "values": [
                    self.red_product_option_value,
                    self.green_product_option_value,
                    self.blue_product_option_value,
                ]
            },
            form.cleaned_data,
        )

    def test_empty_input(self):
        data = {"values": []}
        form = forms.AddProductOptionValuesForm(
            data, edit=self.product_edit, product_option=self.colour_product_option
        )
        self.assert_form_is_valid(form)
        self.assertDictEqual({"values": []}, form.cleaned_data)

    def test_unrecognised_input(self):
        data = {"values": ["New Product Option Value"]}
        form = forms.AddProductOptionValuesForm(
            data, edit=self.product_edit, product_option=self.colour_product_option
        )
        with self.assertRaises(NotImplementedError):
            form.is_valid()

    def test_save_method(self):
        self.assertCountEqual(
            [
                self.red_product_option_value,
                self.green_product_option_value,
                self.blue_product_option_value,
            ],
            self.product_edit.product_option_values.filter(
                product_option=self.colour_product_option
            ),
        )
        cyan = models.ProductOptionValue.objects.create(
            value="Cyan",
            product_option=self.colour_product_option,
            product_option_value_ID="8903483",
        )
        tangerine = models.ProductOptionValue.objects.create(
            value="Tangerine",
            product_option=self.colour_product_option,
            product_option_value_ID="794616",
        )
        data = {"values": [cyan.value, tangerine.value]}
        form = forms.AddProductOptionValuesForm(
            data, edit=self.product_edit, product_option=self.colour_product_option
        )
        self.assert_form_is_valid(form)
        self.assertDictEqual({"values": [cyan, tangerine]}, form.cleaned_data)
        form.save()
        self.assertCountEqual(
            [
                self.red_product_option_value,
                self.green_product_option_value,
                self.blue_product_option_value,
                tangerine,
                cyan,
            ],
            self.product_edit.product_option_values.filter(
                product_option=self.colour_product_option
            ),
        )


class TestSetupVariationsForm(fixtures.EditingProductFixture, FormTest):
    def test_form(self):
        form = forms.SetupVariationsForm()
        self.assertCountEqual(
            [str(_.id) for _ in models.ProductOption.objects.all()],
            list(form.fields.keys()),
        )

    def test_form_submission(self):
        data = {
            str(self.colour_product_option.pk): [
                self.red_product_option_value.value,
                self.green_product_option_value.value,
            ]
        }
        form = forms.SetupVariationsForm(data)
        self.assert_form_is_valid(form)
        self.assertDictEqual(
            {
                self.colour_product_option: [
                    self.red_product_option_value,
                    self.green_product_option_value,
                ],
                self.size_product_option: [],
                self.model_product_option: [],
                self.design_product_option: [],
            },
            form.cleaned_data,
        )

    def test_single_value_is_invalid(self):
        data = {
            str(self.colour_product_option.pk): [self.red_product_option_value.value]
        }
        form = forms.SetupVariationsForm(data)
        self.assert_form_invalid(form)

    def test_submission_with_multiple_product_options(self):
        data = {
            str(self.colour_product_option.pk): [
                self.red_product_option_value.value,
                self.green_product_option_value.value,
            ],
            str(self.size_product_option.pk): [
                self.medium_product_option_value.value,
                self.large_product_option_value.value,
            ],
        }
        form = forms.SetupVariationsForm(data)
        self.assert_form_is_valid(form)
        self.assertDictEqual(
            {
                self.colour_product_option: [
                    self.red_product_option_value,
                    self.green_product_option_value,
                ],
                self.size_product_option: [
                    self.medium_product_option_value,
                    self.large_product_option_value,
                ],
                self.model_product_option: [],
                self.design_product_option: [],
            },
            form.cleaned_data,
        )

    def test_empty_submission(self):
        form = forms.SetupVariationsForm({})
        self.assert_form_is_valid(form)
        self.assertDictEqual(
            {
                self.colour_product_option: [],
                self.size_product_option: [],
                self.model_product_option: [],
                self.design_product_option: [],
            },
            form.cleaned_data,
        )
