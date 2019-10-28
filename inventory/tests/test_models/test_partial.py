from unittest.mock import Mock

from inventory import models
from inventory.tests import fixtures
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestUnique_SKU(STCAdminTest):
    def test_unique_SKU(self):
        function = Mock()
        function.return_value = "RNG_164_DH3-J9L"
        self.assertEqual(models.partial.unique_SKU([], function), "RNG_164_DH3-J9L")

    def test_unique_SKU_retries(self):
        function = Mock()
        function.side_effect = ("RNG_JHL-461-YH5", "RNG_164-DH3-J9L")
        self.assertEqual(
            models.partial.unique_SKU(["RNG_JHL-461-YH5"], function), "RNG_164-DH3-J9L"
        )

    def test_unique_SKU_max_retries(self):
        function = Mock()
        function.return_value = "RNG_164_DH3-J9L"
        with self.assertRaises(Exception):
            models.partial.unique_SKU(["RNG_164_DH3-J9L"], function)


class TestPartialProductRange(STCAdminTest, fixtures.EditingProductFixture):
    fixtures = fixtures.EditingProductFixture.fixtures

    def test_generate_SKU_method(self):
        SKU = models.PartialProductRange.get_new_SKU()
        self.assertEqual(SKU[:4], "RNG_")
        self.assertEqual(len(SKU), 15)

    def test_get_new_SKU_method(self):
        SKU = models.PartialProductRange.get_new_SKU()
        self.assertEqual(SKU[:4], "RNG_")
        self.assertEqual(len(SKU), 15)

    def test_str_method(self):
        self.assertEqual(
            str(self.product_range), f"{self.product_range.SKU} - Test Range"
        )

    def test_has_variations_method(self):
        self.assertTrue(self.product_range.has_variations())

    def test_variation_options_method(self):
        self.assertCountEqual(
            self.product_range.variation_options(),
            [self.size_product_option, self.colour_product_option],
        )

    def test_listing_options_method(self):
        self.assertCountEqual(
            self.product_range.listing_options(), [self.model_product_option]
        )

    def test_product_option_values_method(self):
        self.assertCountEqual(
            self.product_range.product_option_values(),
            [
                self.small_product_option_value,
                self.medium_product_option_value,
                self.large_product_option_value,
                self.red_product_option_value,
                self.blue_product_option_value,
                self.green_product_option_value,
                self.model_product_option_value,
            ],
        )

    def test_variation_option_values_method(self):
        self.assertCountEqual(
            self.product_range.variation_option_values(),
            [
                self.small_product_option_value,
                self.medium_product_option_value,
                self.large_product_option_value,
                self.red_product_option_value,
                self.blue_product_option_value,
                self.green_product_option_value,
            ],
        )

    def test_listing_option_values_method(self):
        self.assertCountEqual(
            self.product_range.listing_option_values(),
            [self.model_product_option_value],
        )

    def test_product_count_method(self):
        self.assertEqual(self.product_range.product_count(), 9)

    def test_products_method(self):
        self.assertCountEqual(
            self.product_range.products(),
            models.PartialProduct.objects.filter(product_range=self.product_range),
        )

    def test_variation_values_method(self):
        variation_values = self.product_range.variation_values()
        self.assertCountEqual(
            list(variation_values.keys()),
            [self.size_product_option, self.colour_product_option],
        )
        self.assertCountEqual(
            variation_values[self.size_product_option],
            [
                self.small_product_option_value,
                self.medium_product_option_value,
                self.large_product_option_value,
            ],
        )
        self.assertCountEqual(
            variation_values[self.colour_product_option],
            [
                self.red_product_option_value,
                self.green_product_option_value,
                self.blue_product_option_value,
            ],
        )

    def test_variations_method(self):
        self.assertEqual(
            self.product_range._variations(),
            [product.variation() for product in self.product_range.products()],
        )

    def test_has_missing_product_option_values_method(self):
        self.assertFalse(self.product_range.has_missing_product_option_values())
        models.PartialProductOptionValueLink.objects.filter(
            product=self.product_range.products()[0]
        )[0].delete()
        self.assertTrue(self.product_range.has_missing_product_option_values())

    def test_all_unique_variations_method(self):
        self.assertTrue(self.product_range.all_unique_variations())
        self.assertTrue(
            self.product_range.all_unique_variations(
                variations=self.product_range._variations()
            )
        )
        models.PartialProductOptionValueLink.objects.filter(
            product=self.product_range.products()[0],
            product_option_value=self.red_product_option_value,
        ).update(product_option_value=self.blue_product_option_value)
        self.assertFalse(self.product_range.all_unique_variations())

    def test_product_options_have_multiple_values_method(self):
        self.assertTrue(self.product_range.product_options_have_multiple_values())
        variations = [
            {
                self.colour_product_option: self.red_product_option_value,
                self.size_product_option: self.large_product_option_value,
            },
            {
                self.colour_product_option: self.red_product_option_value,
                self.size_product_option: self.medium_product_option_value,
            },
            {
                self.colour_product_option: self.red_product_option_value,
                self.size_product_option: self.small_product_option_value,
            },
        ]
        self.assertFalse(
            self.product_range.product_options_have_multiple_values(
                variations=variations
            )
        )

    def test_valid_variations_method(self):
        self.assertTrue(self.product_range.valid_variations())

    def test_valid_variations_method_fails_for_missing_product_options(self):
        models.PartialProductOptionValueLink.objects.filter(
            product=self.product_range.products()[0]
        )[0].delete()
        self.assertFalse(self.product_range.valid_variations())

    def test_valid_variations_method_fails_for_non_unique_variations(self):
        models.PartialProductOptionValueLink.objects.filter(
            product=self.product_range.products()[0],
            product_option_value=self.red_product_option_value,
        ).update(product_option_value=self.blue_product_option_value)
        self.assertFalse(self.product_range.valid_variations())

    def test_valid_variations_method_fails_for_too_few_variation_option_values(self):
        models.PartialProductOptionValueLink.objects.filter(
            product__in=self.product_range.products(),
            product_option_value__product_option=self.colour_product_option,
        ).update(product_option_value=self.blue_product_option_value)
        self.assertFalse(self.product_range.valid_variations())

    def test_range_wide_values_method(self):
        product = self.product_range.products()[0]
        expected = {
            "supplier_id": self.supplier.id,
            "supplier_SKU": product.supplier_SKU,
            "purchase_price": product.purchase_price,
            "VAT_rate_id": self.VAT_rate.id,
            "price": product.price,
            "retail_price": product.retail_price,
            "brand_id": self.brand.id,
            "manufacturer_id": self.manufacturer.id,
            "package_type_id": self.package_type.id,
            "international_shipping_id": self.international_shipping.id,
            "weight_grams": self.product.weight_grams,
            "length_mm": self.product.length_mm,
            "height_mm": self.product.height_mm,
            "width_mm": self.product.width_mm,
            "gender_id": self.gender.id,
        }
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.supplier = models.Supplier.objects.get(id=2)
        product.save()
        expected.pop("supplier_id")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.supplier_SKU = "TY93"
        product.save()
        expected.pop("supplier_SKU")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.purchase_price = 50.89
        product.save()
        expected.pop("purchase_price")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.VAT_rate = models.VATRate.objects.get(id=2)
        product.save()
        expected.pop("VAT_rate_id")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.price = 12.60
        product.save()
        expected.pop("price")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.retail_price = 45.50
        product.save()
        expected.pop("retail_price")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.brand = models.Brand.objects.get(id=2)
        product.save()
        expected.pop("brand_id")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.manufacturer = models.Manufacturer.objects.get(id=2)
        product.save()
        expected.pop("manufacturer_id")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.package_type = models.PackageType.objects.get(id=2)
        product.save()
        expected.pop("package_type_id")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.international_shipping = models.InternationalShipping.objects.get(id=2)
        product.save()
        expected.pop("international_shipping_id")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.weight_grams = 950
        product.save()
        expected.pop("weight_grams")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.length_mm = 540
        product.save()
        expected.pop("length_mm")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.width_mm = 980
        product.save()
        expected.pop("width_mm")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.height_mm = 845
        product.save()
        expected.pop("height_mm")
        self.assertEqual(self.product_range.range_wide_values(), expected)
        product.gender = models.Gender.objects.get(id=2)
        product.save()
        expected.pop("gender_id")
        self.assertEqual(self.product_range.range_wide_values(), {})

    def test_pre_existing_options_method(self):
        self.assertCountEqual(
            self.product_range.pre_existing_options(),
            [
                self.colour_product_option,
                self.size_product_option,
                self.model_product_option,
            ],
        )
        models.PartialProductRangeSelectedOption.objects.filter(
            product_option=self.model_product_option, product_range=self.product_range
        ).update(pre_existing=False)
        self.assertCountEqual(
            self.product_range.pre_existing_options(),
            [self.colour_product_option, self.size_product_option],
        )

    def test_range_bays_match_method(self):
        self.assertEqual(
            list(self.product_range.range_bays_match()),
            [
                self.warehouse_1_bay_1.id,
                self.warehouse_1_bay_2.id,
                self.warehouse_1_bay_3.id,
            ],
        )
        self.product.bays.set([self.warehouse_2_bay_1])
        self.assertIsNone(self.product_range.range_bays_match())


class TestPartialProduct(fixtures.EditingProductFixture, STCAdminTest):
    fixtures = fixtures.EditingProductFixture.fixtures

    def test_generate_SKU_method(self):
        SKU = models.PartialProduct.get_new_SKU()
        self.assertNotEqual(SKU[:4], "RNG_")
        self.assertEqual(len(SKU), 11)

    def test_get_new_SKU_method(self):
        SKU = models.PartialProduct.get_new_SKU()
        self.assertNotEqual(SKU[:4], "RNG_")
        self.assertEqual(len(SKU), 11)

    def test_str_method(self):
        self.assertEqual(
            str(self.product), f"{self.product.SKU}: Test Range - Small - Red - TV009"
        )

    def test_full_name_property(self):
        self.assertEqual(self.product.full_name, "Test Range - Small - Red - TV009")

    def test_full_name_property_without_supplier_SKU(self):
        product = self.product
        product.supplier_SKU = None
        self.assertEqual(product.full_name, "Test Range - Small - Red")

    def test_range_SKU_property(self):
        self.assertEqual(self.product.range_SKU, self.product_range.SKU)

    def test_department_method(self):
        self.assertEqual(self.product.department(), self.product_range.department)

    def test_name_method(self):
        self.assertEqual(self.product.name(), self.product_range.name)

    def test_variation_method(self):
        self.assertEqual(
            self.product.variation(),
            {
                self.colour_product_option: self.red_product_option_value,
                self.size_product_option: self.small_product_option_value,
            },
        )

    def test_variation_method_with_missing_link(self):
        models.PartialProductOptionValueLink.objects.get(
            product=self.product, product_option_value=self.small_product_option_value
        ).delete()
        self.assertIsNone(self.product.variation()[self.size_product_option])

    def test_variable_options_method(self):
        self.assertCountEqual(
            self.product.variable_options(),
            [self.small_product_option_value, self.red_product_option_value],
        )

    def test_listing_options_method(self):
        listing_options = self.product.listing_options()
        self.assertCountEqual(list(listing_options.keys()), [self.model_product_option])
        self.assertEqual(
            listing_options[self.model_product_option], self.model_product_option_value
        )

    def test_name_extensions_method(self):
        self.assertCountEqual(self.product.name_extensions(), ["Small", "Red", "TV009"])

    def test_name_extensions_method_without_supplier_SKU(self):
        product = self.product
        product.supplier_SKU = None
        self.assertCountEqual(product.name_extensions(), ["Small", "Red"])

    def test_product_option_value_method(self):
        self.assertEqual(self.product.product_option_value("Size"), "Small")
        self.assertIsNone(self.product.product_option_value("Quantity"))


class TestPartialProduct_is_complete_Method(
    STCAdminTest, fixtures.EditingProductFixture
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def test_when_complete(self):
        self.assertTrue(self.product.is_complete())

    def test_fails_for_no_SKU(self):
        product = self.product
        product.SKU = None
        product.save()
        self.assertFalse(self.product.is_complete())

    def test_fails_for_no_barcode(self):
        product = self.product
        product.barcode = None
        product.save()
        self.assertFalse(self.product.is_complete())

    def test_fails_for_no_supplier(self):
        product = self.product
        product.supplier = None
        product.save()
        self.assertFalse(self.product.is_complete())

    def test_fails_for_no_purchase_price(self):
        product = self.product
        product.purchase_price = None
        product.save()
        self.assertFalse(self.product.is_complete())

    def test_fails_for_no_VAT_rate(self):
        product = self.product
        product.VAT_rate = None
        product.save()
        self.assertFalse(self.product.is_complete())

    def test_fails_for_no_price(self):
        product = self.product
        product.price = None
        product.save()
        self.assertFalse(self.product.is_complete())

    def test_fails_for_no_brand(self):
        product = self.product
        product.brand = None
        product.save()
        self.assertFalse(self.product.is_complete())

    def test_fails_for_no_manufacturer(self):
        product = self.product
        product.manufacturer = None
        product.save()
        self.assertFalse(self.product.is_complete())

    def test_fails_for_no_package_type(self):
        product = self.product
        product.package_type = None
        product.save()
        self.assertFalse(self.product.is_complete())

    def test_fails_for_no_international_shipping(self):
        product = self.product
        product.international_shipping = None
        product.save()
        self.assertFalse(self.product.is_complete())

    def test_fails_for_no_weight(self):
        product = self.product
        product.weight_grams = None
        product.save()
        self.assertFalse(self.product.is_complete())


class TestPartialProductRangeSelectedOption(
    STCAdminTest, fixtures.EditingProductFixture
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def test_str_method(self):
        selected_option = models.PartialProductRangeSelectedOption.objects.get(
            product_range=self.product_range, product_option=self.size_product_option
        )
        self.assertEqual(
            str(selected_option),
            f"ProductRangeVariableOption: {self.product_range.SKU} - Size",
        )


class TestPartialProductOptionValueLink(STCAdminTest, fixtures.EditingProductFixture):
    fixtures = fixtures.EditingProductFixture.fixtures

    def test_str_method(self):
        option_link = models.PartialProductOptionValueLink.objects.get(
            product=self.product, product_option_value=self.red_product_option_value
        )
        self.assertEqual(
            str(option_link), f"PartialProductOptionValueLink: {self.product.SKU} - Red"
        )


class TestProductEdit(fixtures.EditingProductFixture, STCAdminTest):
    fixtures = fixtures.EditingProductFixture.fixtures

    def test_str_method(self):
        self.assertEqual(str(self.product_edit), str(self.product_range))

    def test_variation_options(self):
        self.assertCountEqual(
            self.product_edit.variation_options(),
            [self.size_product_option, self.colour_product_option],
        )

    def test_delete_method(self):
        product = self.product
        product_range = self.product_range
        edit = self.product_edit
        edit.delete()
        self.assertFalse(models.PartialProduct.objects.filter(id=product.id).exists())
        self.assertFalse(
            models.PartialProductRange.objects.filter(id=product_range.id).exists()
        )
        self.assertFalse(models.ProductEdit.objects.filter(id=edit.id).exists())

    def test_create_product_method(self):
        self.product.delete()
        product = self.product_edit.create_product(
            (self.small_product_option_value, self.red_product_option_value)
        )
        self.assertTrue(models.PartialProduct.objects.filter(id=product.id).exists())
        self.assertEqual(product.product_range, self.product_range)
        self.assertEqual(
            product.product_option_value("Size"), self.small_product_option_value.value
        )
        self.assertEqual(
            product.product_option_value("Colour"), self.red_product_option_value.value
        )
        self.assertEqual(len(product.SKU), 11)
        self.assertIsNotNone(product.date_created)
        self.assertEqual(product.supplier, self.supplier)
