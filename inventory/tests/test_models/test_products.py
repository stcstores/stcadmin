from decimal import Decimal
from unittest.mock import patch

from inventory import models
from inventory.tests import fixtures
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestSingleProduct(fixtures.SingleProductRangeFixture, STCAdminTest):
    def test_properties(self):
        self.assertEqual("724587", self.product.product_ID)
        self.assertEqual(self.product_range, self.product.product_range)
        self.assertEqual(11, len(self.product.SKU))
        self.assertEqual(self.supplier, self.product.supplier)
        self.assertEqual("TV009", self.product.supplier_SKU)
        self.assertEqual("29485839", self.product.barcode)
        self.assertEqual(Decimal("5.60"), self.product.purchase_price)
        self.assertEqual(self.VAT_rate, self.product.VAT_rate)
        self.assertEqual(Decimal("6.80"), self.product.price)
        self.assertEqual(Decimal("12.70"), self.product.retail_price)
        self.assertEqual(self.brand, self.product.brand)
        self.assertEqual(self.manufacturer, self.product.manufacturer)
        self.assertEqual(self.package_type, self.product.package_type)
        self.assertEqual(
            self.international_shipping, self.product.international_shipping
        )
        self.assertEqual(self.gender, self.product.gender)
        self.assertEqual(500, self.product.weight_grams)
        self.assertEqual(50, self.product.length_mm)
        self.assertEqual(150, self.product.height_mm)
        self.assertEqual(24, self.product.width_mm)
        self.assertIsNotNone(self.product.date_created)

    def test_str_method(self):
        self.assertEqual(str(self.product), f"{self.product.SKU}: Test Range - TV009")

    def test_full_name_property(self):
        self.assertEqual(self.product.full_name, "Test Range - TV009")

    def test_full_name_property_without_supplier_SKU(self):
        self.product.supplier_SKU = None
        self.assertEqual(self.product.full_name, "Test Range")

    def test_range_SKU_property(self):
        self.assertEqual(self.product.range_SKU, self.product_range.SKU)

    def test_department_method(self):
        self.assertEqual(self.product.department(), self.product_range.department)

    def test_name_method(self):
        self.assertEqual(self.product.name(), self.product_range.name)

    def test_variation_method(self):
        self.assertEqual(self.product.variation(), {})

    def test_variable_options_method(self):
        self.assertCountEqual(self.product.variable_options(), [])

    def test_listing_options_method(self):
        self.assertEqual(self.product.listing_options(), {})

    def test_name_extensions_method(self):
        self.assertCountEqual(self.product.name_extensions(), ["TV009"])

    def test_name_extensions_method_without_supplier_SKU(self):
        self.product.supplier_SKU = None
        self.assertCountEqual(self.product.name_extensions(), [])

    def test_product_option_value_method(self):
        self.assertIsNone(self.product.product_option_value("Size"))


class TestSingleProductRange(fixtures.SingleProductRangeFixture, STCAdminTest):
    def test_str_method(self):
        self.assertEqual(
            str(self.product_range), f"{self.product_range.SKU} - Test Range"
        )

    def test_has_variations_method(self):
        self.assertFalse(self.product_range.has_variations())

    def test_variation_options_method(self):
        self.assertCountEqual(self.product_range.variation_options(), [])

    def test_listing_options_method(self):
        self.assertCountEqual(self.product_range.listing_options(), [])

    def test_product_option_values_method(self):
        self.assertCountEqual(self.product_range.product_option_values(), [])

    def test_variation_option_values_method(self):
        self.assertCountEqual(self.product_range.variation_option_values(), [])

    def test_listing_option_values_method(self):
        self.assertCountEqual(self.product_range.listing_option_values(), [])

    def test_product_count_method(self):
        self.assertEqual(self.product_range.product_count(), 1)

    def test_products_method(self):
        self.assertCountEqual(self.product_range.products(), [self.product])

    def test_variation_values_method(self):
        self.assertEqual(self.product_range.variation_values(), {})


class TestVariationProductRange(fixtures.VariationProductRangeFixture, STCAdminTest):
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
            models.Product.objects.filter(product_range=self.product_range),
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


class TestVariationProduct(fixtures.VariationProductRangeFixture, STCAdminTest):
    def test_properties(self):
        for product in self.product_range.products():
            self.assertEqual(self.product_range, product.product_range)
            self.assertEqual(11, len(product.SKU))
            self.assertEqual(self.supplier, product.supplier)
            self.assertEqual("TV009", product.supplier_SKU)
            self.assertEqual("29485839", product.barcode)
            self.assertEqual(Decimal("5.60"), self.product.purchase_price)
            self.assertEqual(self.VAT_rate, self.product.VAT_rate)
            self.assertEqual(Decimal("6.80"), self.product.price)
            self.assertEqual(Decimal("12.70"), self.product.retail_price)
            self.assertEqual(self.brand, product.brand)
            self.assertEqual(self.manufacturer, product.manufacturer)
            self.assertEqual(self.package_type, product.package_type)
            self.assertEqual(
                self.international_shipping, product.international_shipping
            )
            self.assertEqual(self.gender, product.gender)
            self.assertEqual(500, product.weight_grams)
            self.assertEqual(50, product.length_mm)
            self.assertEqual(150, product.height_mm)
            self.assertEqual(24, product.width_mm)
            self.assertIsNotNone(product.date_created)

    def test_str_method(self):
        self.assertEqual(
            str(self.product), f"{self.product.SKU}: Test Range - Small - Red - TV009"
        )

    def test_full_name_property(self):
        self.assertEqual(self.product.full_name, "Test Range - Small - Red - TV009")

    def test_full_name_property_without_supplier_SKU(self):
        self.product.supplier_SKU = None
        self.assertEqual(self.product.full_name, "Test Range - Small - Red")

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
        models.ProductOptionValueLink.objects.get(
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
        self.product.supplier_SKU = None
        self.assertCountEqual(self.product.name_extensions(), ["Small", "Red"])

    def test_product_option_value_method(self):
        self.assertEqual(self.product.product_option_value("Size"), "Small")
        self.assertIsNone(self.product.product_option_value("Quantity"))

    @patch("inventory.models.products.CCAPI")
    def test_stock_level_method(self, mock_CCAPI):
        self.product.stock_level()
        mock_CCAPI.get_product.assert_called_with(self.product.product_ID)

    @patch("inventory.models.products.CCAPI")
    def test_update_stock_level_method(self, mock_CCAPI):
        self.product.update_stock_level(old=5, new=6)
        mock_CCAPI.update_product_stock_level.assert_called_with(
            product_id=self.product.product_ID, old_stock_level=5, new_stock_level=6
        )


class TestProductRangeSelectedOptionModel(
    fixtures.VariationProductRangeFixture, STCAdminTest
):
    def test_str_method(self):
        link = models.ProductRangeSelectedOption.objects.get(
            product_range=self.product_range, product_option=self.size_product_option
        )
        self.assertEqual(
            str(link), f"ProductRangeVariableOption: {self.product_range.SKU} - Size"
        )


class TestProductOptionValueLinkModel(
    fixtures.VariationProductRangeFixture, STCAdminTest
):
    def test_str_method(self):
        link = models.ProductOptionValueLink.objects.get(
            product=self.product, product_option_value=self.small_product_option_value
        )
        self.assertEqual(
            str(link), f"ProductOptionValueLink: {self.product.SKU} - Small"
        )
