import itertools
from unittest.mock import patch

from django.test import TestCase

from inventory import models


class SetupProducts:
    def setUp(self):
        super().setUp()
        self.create_departments()
        self.create_suppliers()
        self.create_VAT_rates()
        self.create_brands()
        self.create_manufacturers()
        self.create_package_types()
        self.create_international_shipping()
        self.create_product_options()
        self.create_ranges()
        self.add_products()

    def tearDown(self):
        models.ProductOptionValueLink.objects.all().delete()
        models.ProductRangeSelectedOption.objects.all().delete()
        models.ProductOptionValue.objects.all().delete()
        models.Product.objects.all().delete()
        models.ProductRange.objects.all().delete()
        models.ProductOption.objects.all().delete()
        super().tearDown()

    def create_departments(self):
        self.department = models.Department.objects.create(
            name="Test Department", product_option_value_ID="8394"
        )

    def create_suppliers(self):
        self.supplier = models.Supplier.objects.create(
            name="Shop Inc", product_option_value_ID="289493", factory_ID="164868"
        )

    def create_VAT_rates(self):
        self.VAT_rate = models.VATRate.objects.create(
            VAT_rate_ID="0", name="Basic", percentage=0.2
        )

    def create_brands(self):
        self.brand = models.Brand.objects.create(
            name="Shop Inc", product_option_value_ID="394503"
        )

    def create_manufacturers(self):
        self.manufacturer = models.Manufacturer.objects.create(
            name="Shop Inc", product_option_value_ID="394584"
        )

    def create_package_types(self):
        self.package_type = models.PackageType.objects.create(
            name="Basic Shipping",
            product_option_value_ID="398540",
            large_letter_compatible=False,
        )

    def create_international_shipping(self):
        self.international_shipping = models.InternationalShipping.objects.create(
            name="Standard", product_option_value_ID="26578"
        )

    def create_product_options(self):
        self.size_product_option = models.ProductOption.objects.create(
            name="Size", product_option_ID="3833", sort_order=0
        )
        self.colour_product_option = models.ProductOption.objects.create(
            name="Colour", product_option_ID="3835", sort_order=1
        )
        self.model_product_option = models.ProductOption.objects.create(
            name="Model", product_option_ID="7651", sort_order=2
        )
        self.red_product_option_value = models.ProductOptionValue.objects.create(
            value="Red",
            product_option=self.colour_product_option,
            product_option_value_ID="39495",
        )
        self.green_product_option_value = models.ProductOptionValue.objects.create(
            value="Green",
            product_option=self.colour_product_option,
            product_option_value_ID="39484",
        )
        self.blue_product_option_value = models.ProductOptionValue.objects.create(
            value="Blue",
            product_option=self.colour_product_option,
            product_option_value_ID="39464",
        )
        self.small_product_option_value = models.ProductOptionValue.objects.create(
            value="Small",
            product_option=self.size_product_option,
            product_option_value_ID="59303",
        )
        self.medium_product_option_value = models.ProductOptionValue.objects.create(
            value="Medium",
            product_option=self.size_product_option,
            product_option_value_ID="59398",
        )
        self.large_product_option_value = models.ProductOptionValue.objects.create(
            value="Large",
            product_option=self.size_product_option,
            product_option_value_ID="59384",
        )
        self.model_product_option_value = models.ProductOptionValue.objects.create(
            value="DB25",
            product_option=self.model_product_option,
            product_option_value_ID="549681",
        )

    def new_product_range(self):
        return models.ProductRange(
            range_ID=self.RANGE_ID,
            SKU="RNG_A8D_D83_NFU",
            name="Test Range",
            department=self.department,
            description="A test product\nLine Two",
            amazon_bullet_points=(
                "Dad's Army - Service Issue Mug.|Ceramic Boxed Mug.|"
                "Height: 11 cm x Width: 8 cm approx.|Officially Licensed Product."
            ),
            amazon_search_terms="Ceramic Mug|Dad's Army",
        )

    def new_product(self, product_range):
        return models.Product(
            product_ID="0",
            product_range=product_range,
            SKU=models.PartialProduct.generate_SKU(),
            supplier=self.supplier,
            supplier_SKU="TV009",
            barcode="29485839",
            purchase_price=5.60,
            VAT_rate=self.VAT_rate,
            price=6.80,
            retail_price=12.70,
            brand=self.brand,
            manufacturer=self.manufacturer,
            package_type=self.package_type,
            international_shipping=self.international_shipping,
            weight_grams=500,
            length_mm=50,
            height_mm=150,
            width_mm=24,
        )


class SetupSingleProductRange(SetupProducts):
    RANGE_ID = "548354"
    maxDiff = None

    def create_ranges(self):
        self.product_range = self.new_product_range()
        self.product_range.range_ID = self.RANGE_ID
        self.product_range.save()

    def add_products(self):
        self.product = self.new_product(self.product_range)
        self.product.product_ID = "724587"
        self.product.save()


class SetupVariationProductRange(SetupProducts):
    RANGE_ID = "389839"
    maxDiff = None

    def create_ranges(self):
        self.product_range = models.ProductRange.objects.create(
            range_ID=self.RANGE_ID,
            SKU="RNG_A8D_D83_NFU",
            name="Test Range",
            department=self.department,
            description="A test product\nLine Two",
            amazon_bullet_points=(
                "Dad's Army - Service Issue Mug.|Ceramic Boxed Mug.|"
                "Height: 11 cm x Width: 8 cm approx.|Officially Licensed Product."
            ),
            amazon_search_terms="Ceramic Mug|Dad's Army",
        )
        models.ProductRangeSelectedOption.objects.create(
            product_range=self.product_range,
            product_option=self.size_product_option,
            variation=True,
        )
        models.ProductRangeSelectedOption.objects.create(
            product_range=self.product_range,
            product_option=self.colour_product_option,
            variation=True,
        )
        models.ProductRangeSelectedOption.objects.create(
            product_range=self.product_range,
            product_option=self.model_product_option,
            variation=False,
        )

    def add_products(self):
        self.variations = []
        options = [
            [
                self.small_product_option_value,
                self.medium_product_option_value,
                self.large_product_option_value,
            ],
            [
                self.red_product_option_value,
                self.green_product_option_value,
                self.blue_product_option_value,
            ],
        ]
        for i, options in enumerate(itertools.product(*options)):
            product = self.new_product(self.product_range)
            product.product_ID = str(93943 + i)
            product.save()
            for option in options:
                models.ProductOptionValueLink.objects.create(
                    product=product, product_option_value=option
                )
            models.ProductOptionValueLink.objects.create(
                product=product, product_option_value=self.model_product_option_value
            )
            self.variations.append(product)
        self.product = self.variations[0]


class TestSingleProduct(SetupSingleProductRange, TestCase):
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


class TestSingleProductRange(SetupSingleProductRange, TestCase):
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


class TestVariationProductRange(SetupVariationProductRange, TestCase):
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


class TestVariationProduct(SetupVariationProductRange, TestCase):
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


class TestProductRangeSelectedOptionModel(SetupVariationProductRange, TestCase):
    def test_str_method(self):
        link = models.ProductRangeSelectedOption.objects.get(
            product_range=self.product_range, product_option=self.size_product_option
        )
        self.assertEqual(
            str(link), f"ProductRangeVariableOption: {self.product_range.SKU} - Size"
        )


class TestProductOptionValueLinkModel(SetupVariationProductRange, TestCase):
    def test_str_method(self):
        link = models.ProductOptionValueLink.objects.get(
            product=self.product, product_option_value=self.small_product_option_value
        )
        self.assertEqual(
            str(link), f"ProductOptionValueLink: {self.product.SKU} - Small"
        )
