import itertools
from decimal import Decimal
from unittest.mock import patch

from inventory import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class SetupProducts:
    def setUp(self):
        super().setUp()
        self.product_range = models.ProductRange.objects.get(SKU=self.product_range.SKU)
        self.product = models.Product.objects.get(SKU=self.product.SKU)

    @classmethod
    def setUpTestData(cls):
        cls.create_departments()
        cls.create_suppliers()
        cls.create_VAT_rates()
        cls.create_brands()
        cls.create_manufacturers()
        cls.create_package_types()
        cls.create_international_shipping()
        cls.create_gender()
        cls.create_product_options()
        cls.create_ranges()
        cls.add_products()

    @classmethod
    def create_departments(cls):
        cls.department = models.Department.objects.create(
            name="Test Department", product_option_value_ID="8394"
        )
        cls.other_department = models.Department.objects.create(
            name="Sports", product_option_value_ID="8384"
        )

    @classmethod
    def create_suppliers(cls):
        cls.supplier = models.Supplier.objects.create(
            name="Shop Inc", product_option_value_ID="289493", factory_ID="164868"
        )
        cls.other_supplier = models.Supplier.objects.create(
            name="Wholesale", product_option_value_ID="289485", factory_ID="164416"
        )

    @classmethod
    def create_VAT_rates(cls):
        cls.VAT_rate = models.VATRate.objects.create(
            VAT_rate_ID="0", name="Basic", percentage=0.2
        )
        cls.other_VAT_rate = models.VATRate.objects.create(
            VAT_rate_ID="5", name="VAT Free", percentage=0
        )

    @classmethod
    def create_brands(cls):
        cls.brand = models.Brand.objects.create(
            name="Shop Inc", product_option_value_ID="394503"
        )
        cls.other_brand = models.Brand.objects.create(
            name="Shoes Shop", product_option_value_ID="394746"
        )

    @classmethod
    def create_manufacturers(cls):
        cls.manufacturer = models.Manufacturer.objects.create(
            name="Shop Inc", product_option_value_ID="394565"
        )
        cls.other_manufacturer = models.Manufacturer.objects.create(
            name="Shoes Shop", product_option_value_ID="394584"
        )

    @classmethod
    def create_package_types(cls):
        cls.package_type = models.PackageType.objects.create(
            name="Basic Shipping",
            product_option_value_ID="398540",
            large_letter_compatible=False,
        )
        cls.other_package_type = models.PackageType.objects.create(
            name="Express Shipping",
            product_option_value_ID="398456",
            large_letter_compatible=True,
        )

    @classmethod
    def create_international_shipping(cls):
        cls.international_shipping = models.InternationalShipping.objects.create(
            name="Standard", product_option_value_ID="26578"
        )
        cls.other_international_shipping = models.InternationalShipping.objects.create(
            name="Express", product_option_value_ID="26587"
        )

    @classmethod
    def create_gender(cls):
        cls.gender = models.Gender.objects.create(
            name="mens", readable_name="Mens", product_option_value_ID="416164"
        )
        cls.other_gender = models.Gender.objects.create(
            name="womens", readable_name="Womens", product_option_value_ID="416115"
        )

    @classmethod
    def create_product_options(cls):
        cls.size_product_option = models.ProductOption.objects.create(
            name="Size", product_option_ID="3833", sort_order=0
        )
        cls.colour_product_option = models.ProductOption.objects.create(
            name="Colour", product_option_ID="3835", sort_order=1
        )
        cls.model_product_option = models.ProductOption.objects.create(
            name="Model", product_option_ID="7651", sort_order=2
        )
        cls.red_product_option_value = models.ProductOptionValue.objects.create(
            value="Red",
            product_option=cls.colour_product_option,
            product_option_value_ID="39495",
        )
        cls.green_product_option_value = models.ProductOptionValue.objects.create(
            value="Green",
            product_option=cls.colour_product_option,
            product_option_value_ID="39484",
        )
        cls.blue_product_option_value = models.ProductOptionValue.objects.create(
            value="Blue",
            product_option=cls.colour_product_option,
            product_option_value_ID="39464",
        )
        cls.small_product_option_value = models.ProductOptionValue.objects.create(
            value="Small",
            product_option=cls.size_product_option,
            product_option_value_ID="59303",
        )
        cls.medium_product_option_value = models.ProductOptionValue.objects.create(
            value="Medium",
            product_option=cls.size_product_option,
            product_option_value_ID="59398",
        )
        cls.large_product_option_value = models.ProductOptionValue.objects.create(
            value="Large",
            product_option=cls.size_product_option,
            product_option_value_ID="59384",
        )
        cls.model_product_option_value = models.ProductOptionValue.objects.create(
            value="DB25",
            product_option=cls.model_product_option,
            product_option_value_ID="549681",
        )

    @classmethod
    def new_product_range(cls):
        return models.ProductRange(
            range_ID=cls.RANGE_ID,
            SKU="RNG_A8D_D83_NFU",
            name="Test Range",
            department=cls.department,
            description="A test product\nLine Two",
            amazon_bullet_points=(
                "Dad's Army - Service Issue Mug.|Ceramic Boxed Mug.|"
                "Height: 11 cm x Width: 8 cm approx.|Officially Licensed Product."
            ),
            amazon_search_terms="Ceramic Mug|Dad's Army",
        )

    @classmethod
    def new_product(cls, product_range):
        return models.Product(
            product_ID="0",
            product_range=product_range,
            SKU=models.PartialProduct.generate_SKU(),
            supplier=cls.supplier,
            supplier_SKU="TV009",
            barcode="29485839",
            purchase_price=5.60,
            VAT_rate=cls.VAT_rate,
            price=6.80,
            retail_price=12.70,
            brand=cls.brand,
            manufacturer=cls.manufacturer,
            package_type=cls.package_type,
            international_shipping=cls.international_shipping,
            gender=cls.gender,
            weight_grams=500,
            length_mm=50,
            height_mm=150,
            width_mm=24,
        )


class SetupSingleProductRange(SetupProducts):
    RANGE_ID = "548354"
    maxDiff = None

    @classmethod
    def create_ranges(cls):
        cls.product_range = cls.new_product_range()
        cls.product_range.range_ID = cls.RANGE_ID
        cls.product_range.save()

    @classmethod
    def add_products(cls):
        cls.product = cls.new_product(cls.product_range)
        cls.product.product_ID = "724587"
        cls.product.save()
        cls.product = models.Product.objects.get(id=cls.product.id)


class SetupVariationProductRange(SetupProducts):
    RANGE_ID = "389839"
    maxDiff = None

    @classmethod
    def create_ranges(cls):
        cls.product_range = models.ProductRange.objects.create(
            range_ID=cls.RANGE_ID,
            SKU="RNG_A8D_D83_NFU",
            name="Test Range",
            department=cls.department,
            description="A test product\nLine Two",
            amazon_bullet_points=(
                "Dad's Army - Service Issue Mug.|Ceramic Boxed Mug.|"
                "Height: 11 cm x Width: 8 cm approx.|Officially Licensed Product."
            ),
            amazon_search_terms="Ceramic Mug|Dad's Army",
        )
        models.ProductRangeSelectedOption.objects.create(
            product_range=cls.product_range,
            product_option=cls.size_product_option,
            variation=True,
        )
        models.ProductRangeSelectedOption.objects.create(
            product_range=cls.product_range,
            product_option=cls.colour_product_option,
            variation=True,
        )
        models.ProductRangeSelectedOption.objects.create(
            product_range=cls.product_range,
            product_option=cls.model_product_option,
            variation=False,
        )

    @classmethod
    def add_products(cls):
        cls.variations = []
        options = [
            [
                cls.small_product_option_value,
                cls.medium_product_option_value,
                cls.large_product_option_value,
            ],
            [
                cls.red_product_option_value,
                cls.green_product_option_value,
                cls.blue_product_option_value,
            ],
        ]
        for i, options in enumerate(itertools.product(*options)):
            product = cls.new_product(cls.product_range)
            product.product_ID = str(93943 + i)
            product.save()
            for option in options:
                models.ProductOptionValueLink.objects.create(
                    product=product, product_option_value=option
                )
            models.ProductOptionValueLink.objects.create(
                product=product, product_option_value=cls.model_product_option_value
            )
            cls.variations.append(product)
        cls.product = models.Product.objects.get(id=cls.variations[0].id)


class TestSingleProduct(SetupSingleProductRange, STCAdminTest):
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
        # models.Product(
        #     product_ID="0",
        #     product_range=product_range,
        #     SKU=models.PartialProduct.generate_SKU(),
        #     supplier=cls.supplier,
        #     supplier_SKU="TV009",
        #     barcode="29485839",
        #     purchase_price=5.60,
        #     VAT_rate=cls.VAT_rate,
        #     price=6.80,
        #     retail_price=12.70,
        #     brand=cls.brand,
        #     manufacturer=cls.manufacturer,
        #     package_type=cls.package_type,
        #     international_shipping=cls.international_shipping,
        #     gender=cls.gender,
        #     weight_grams=500,
        #     length_mm=50,
        #     height_mm=150,
        #     width_mm=24,
        # )

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


class TestSingleProductRange(SetupSingleProductRange, STCAdminTest):
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


class TestVariationProductRange(SetupVariationProductRange, STCAdminTest):
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


class TestVariationProduct(SetupVariationProductRange, STCAdminTest):
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


class TestProductRangeSelectedOptionModel(SetupVariationProductRange, STCAdminTest):
    def test_str_method(self):
        link = models.ProductRangeSelectedOption.objects.get(
            product_range=self.product_range, product_option=self.size_product_option
        )
        self.assertEqual(
            str(link), f"ProductRangeVariableOption: {self.product_range.SKU} - Size"
        )


class TestProductOptionValueLinkModel(SetupVariationProductRange, STCAdminTest):
    def test_str_method(self):
        link = models.ProductOptionValueLink.objects.get(
            product=self.product, product_option_value=self.small_product_option_value
        )
        self.assertEqual(
            str(link), f"ProductOptionValueLink: {self.product.SKU} - Small"
        )
