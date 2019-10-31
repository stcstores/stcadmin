from decimal import Decimal
from unittest.mock import Mock, call, patch

from inventory import models
from inventory.cloud_commerce_updater import SaveEdit
from inventory.tests import fixtures
from stcadmin.tests.stcadmin_test import STCAdminTest


class BaseSaveEditTest:
    @classmethod
    def setUpTestData(cls):
        STCAdminTest.create_user()

    def setUp(self):
        self.setup_mocks()

    def setup_mocks(self):
        ccapi_patcher = patch("inventory.cloud_commerce_updater.save_edit.CCAPI")
        range_updater_patcher = patch(
            "inventory.cloud_commerce_updater.save_edit.RangeUpdater"
        )
        product_updater_patcher = patch(
            "inventory.cloud_commerce_updater.save_edit.ProductUpdater"
        )
        self.mock_CCAPI = ccapi_patcher.start()
        self.mock_RangeUpdater = range_updater_patcher.start()
        self.mock_ProductUpdater = product_updater_patcher.start()
        self.addCleanup(range_updater_patcher.stop)
        self.addCleanup(product_updater_patcher.stop)
        self.addCleanup(ccapi_patcher.stop)
        self.mock_range_updater = Mock()
        self.mock_RangeUpdater.return_value = self.mock_range_updater
        self.mock_product_updater = Mock()
        self.mock_ProductUpdater.return_value = self.mock_product_updater


class TestSaveEditForNewRange(
    BaseSaveEditTest, STCAdminTest, fixtures.EditingProductFixture
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def test_save_edit(self):
        save_edit = SaveEdit(self.product_edit, self.user)
        self.assertEqual(self.product_edit, save_edit.edit)
        self.assertEqual(self.user, save_edit.user)
        save_edit.save_edit()
        self.assertEqual(self.original_range, save_edit.original_range)
        self.assertEqual(self.product_range, save_edit.partial_range)
        self.assertEqual(self.mock_range_updater, save_edit.range_updater)
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.assertEqual(0, len(self.mock_product_updater.mock_calls))

    def test_set_range_name(self):
        name = "New Range Name"
        product_range = self.product_range
        product_range.name = name
        product_range.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.mock_range_updater.set_name.assert_called_once_with(name)
        self.assertEqual(3, len(self.mock_range_updater.mock_calls))
        self.assertEqual(0, len(self.mock_product_updater.mock_calls))

    def test_set_department(self):
        department = self.second_department
        product_range = self.product_range
        product_range.department = department
        product_range.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.mock_range_updater.set_department.assert_called_once_with(department)
        self.assertEqual(3, len(self.mock_range_updater.mock_calls))
        self.assertEqual(0, len(self.mock_product_updater.mock_calls))

    def test_set_description(self):
        description = "New Description\nFor the product range."
        product_range = self.product_range
        product_range.description = description
        product_range.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.mock_range_updater.set_description.assert_called_once_with(description)
        self.assertEqual(3, len(self.mock_range_updater.mock_calls))
        self.assertEqual(0, len(self.mock_product_updater.mock_calls))

    def test_set_amazon_search_terms(self):
        search_terms = "mug|cup"
        product_range = self.product_range
        product_range.amazon_search_terms = search_terms
        product_range.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.mock_range_updater.set_amazon_search_terms.assert_called_once_with(
            search_terms
        )
        self.assertEqual(3, len(self.mock_range_updater.mock_calls))
        self.assertEqual(0, len(self.mock_product_updater.mock_calls))

    def test_set_amazon_bullet_points(self):
        bullets = "mug|cup"
        product_range = self.product_range
        product_range.amazon_bullet_points = bullets
        product_range.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.mock_range_updater.set_amazon_bullet_points.assert_called_once_with(
            bullets
        )
        self.assertEqual(3, len(self.mock_range_updater.mock_calls))
        self.assertEqual(0, len(self.mock_product_updater.mock_calls))

    def test_set_supplier(self):
        new_supplier = self.second_supplier
        product = self.product
        product.supplier = new_supplier
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_supplier.assert_called_once_with(new_supplier)
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_supplier_SKU(self):
        new_supplier_SKU = "BN0383"
        product = self.product
        product.supplier_SKU = new_supplier_SKU
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_supplier_SKU.assert_called_once_with(
            new_supplier_SKU
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_barcode(self):
        new_barcode = "0387547393"
        product = self.product
        product.barcode = new_barcode
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_barcode.assert_called_once_with(new_barcode)
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_purchase_price(self):
        new_purchase_price = 5.99
        product = self.product
        product.purchase_price = new_purchase_price
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_purchase_price.assert_called_once_with(
            Decimal(str(new_purchase_price))
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_VAT_rate(self):
        new_VAT_rate = self.second_VAT_rate
        product = self.product
        product.VAT_rate = new_VAT_rate
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_VAT_rate.assert_called_once_with(new_VAT_rate)
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_price(self):
        new_price = 8.74
        product = self.product
        product.price = new_price
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_price.assert_called_once_with(
            Decimal(str(new_price))
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_retail_price(self):
        new_price = 8.74
        product = self.product
        product.retail_price = new_price
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_retail_price.assert_called_once_with(
            Decimal(str(new_price))
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_brand(self):
        new_brand = self.second_brand
        product = self.product
        product.brand = new_brand
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_brand.assert_called_once_with(new_brand)
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_manufacturer(self):
        new_manufacturer = self.second_manufacturer
        product = self.product
        product.manufacturer = new_manufacturer
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_manufacturer.assert_called_once_with(
            new_manufacturer
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_package_type(self):
        new_package_type = self.second_package_type
        product = self.product
        product.package_type = new_package_type
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_package_type.assert_called_once_with(
            new_package_type
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_international_shipping(self):
        international_shipping = self.second_international_shipping
        product = self.product
        product.international_shipping = international_shipping
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_international_shipping.assert_called_once_with(
            international_shipping
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_weight(self):
        weight = 584
        product = self.product
        product.weight_grams = weight
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_weight.assert_called_once_with(weight)
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_length(self):
        length = 1150
        product = self.product
        product.length_mm = length
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_length.assert_called_once_with(length)
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_width(self):
        width = 860
        product = self.product
        product.width_mm = width
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_width.assert_called_once_with(width)
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_height(self):
        height = 51
        product = self.product
        product.height_mm = height
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_height.assert_called_once_with(height)
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_gender(self):
        gender = self.second_gender
        product = self.product
        product.gender = gender
        product.save()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_gender.assert_called_once_with(gender)
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_set_bays(self):
        bays = [self.warehouse_1_bay_1, self.warehouse_1_bay_2]
        self.product.bays.set(bays)
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_bays.assert_called_once_with(bays)
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_change_option_links(self):
        models.PartialProductOptionValueLink.objects.filter(
            product=self.product,
            product_option_value__product_option=self.size_product_option,
        ).delete()
        product_option_value = models.ProductOptionValueLink.objects.get(
            product=self.original_range.products()[0],
            product_option_value__product_option=self.size_product_option,
        ).product_option_value
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(2, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.remove_product_option.assert_called_once_with(
            product_option_value
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_add_listing_option_links(self):
        product_option = models.ProductOption.objects.create(
            name="Shape", product_option_ID="84832"
        )
        product_option_value = models.ProductOptionValue.objects.create(
            value="Round",
            product_option=product_option,
            product_option_value_ID="385938",
        )
        models.PartialProductRangeSelectedOption.objects.create(
            product_range=self.product_range,
            product_option=product_option,
            variation=False,
        )
        models.PartialProductOptionValueLink.objects.create(
            product=self.product, product_option_value=product_option_value
        )
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.mock_range_updater.add_listing_product_option.assert_called_once_with(
            product_option
        )
        self.assertEqual(3, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_product_option_link.assert_called_once_with(
            product_option_value
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_add_variation_option_links(self):
        product_option = models.ProductOption.objects.create(
            name="Shape", product_option_ID="84832"
        )
        product_option_value = models.ProductOptionValue.objects.create(
            value="Round",
            product_option=product_option,
            product_option_value_ID="385938",
        )
        models.PartialProductRangeSelectedOption.objects.create(
            product_range=self.product_range,
            product_option=product_option,
            variation=True,
        )
        models.PartialProductOptionValueLink.objects.create(
            product=self.product, product_option_value=product_option_value
        )
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.mock_range_updater.add_variation_product_option.assert_called_once_with(
            product_option
        )
        self.assertEqual(3, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.set_product_option_link.assert_called_once_with(
            product_option_value
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_remove_variation_option_links(self):
        models.PartialProductOptionValueLink.objects.filter(
            product=self.product, product_option_value=self.small_product_option_value
        ).delete()
        models.PartialProductRangeSelectedOption.objects.filter(
            product_range=self.product_range, product_option=self.size_product_option
        ).delete()
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.mock_range_updater.remove_product_option.assert_called_once_with(
            self.size_product_option
        )
        self.assertEqual(3, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.remove_product_option.assert_called_once_with(
            self.small_product_option_value
        )
        self.assertEqual(1, len(self.mock_product_updater.mock_calls))

    def test_remove_listing_option_links(self):
        product_option = models.ProductOption.objects.create(
            name="Shape", product_option_ID="84832"
        )
        product_option_value = models.ProductOptionValue.objects.create(
            value="Round",
            product_option=product_option,
            product_option_value_ID="385938",
        )
        models.ProductRangeSelectedOption.objects.create(
            product_range=self.original_range,
            product_option=product_option,
            variation=False,
        )
        for product in self.original_range.products():
            models.ProductOptionValueLink.objects.create(
                product=product, product_option_value=product_option_value
            )
        SaveEdit(self.product_edit, self.user).save_edit()
        self.assertEqual(2, len(self.mock_range_updater.log.mock_calls))
        self.mock_range_updater.remove_product_option.assert_called_once_with(
            product_option
        )
        product_count = self.original_range.products().count()
        self.assertEqual(3, len(self.mock_range_updater.mock_calls))
        self.mock_product_updater.remove_product_option.assert_has_calls(
            [call(product_option_value) for _ in range(product_count)]
        )
        self.assertEqual(product_count, len(self.mock_product_updater.mock_calls))


class TestSaveEditWithNewProduct(
    BaseSaveEditTest, STCAdminTest, fixtures.EditingProductFixture
):
    fixtures = fixtures.EditingProductFixture.fixtures

    @classmethod
    def setUpTestData(cls):
        STCAdminTest.create_user()
        models.Product.objects.get(id=1).delete()

    def setUp(self):
        product = self.product
        product.pre_existing = False
        product.barcode = "385493829"
        self.setup_mocks()
        product.save()

    def setup_mocks(self):
        super().setup_mocks()
        self.new_product_ID = "2849382"
        self.mock_CCAPI.create_product.return_value = self.new_product_ID

    def test_new_database_product(self):
        SaveEdit(self.product_edit, self.user).save_edit()
        new_product = models.Product.objects.get(SKU=self.product.SKU)
        self.assertEqual(self.new_product_ID, new_product.product_ID)
        self.assertEqual(self.original_range, new_product.product_range)
        comparison_attributes = (
            "supplier",
            "supplier_SKU",
            "barcode",
            "purchase_price",
            "VAT_rate",
            "price",
            "retail_price",
            "brand",
            "manufacturer",
            "package_type",
            "international_shipping",
            "weight_grams",
            "length_mm",
            "height_mm",
            "width_mm",
        )
        for attribute in comparison_attributes:
            self.assertEqual(
                getattr(self.product, attribute), getattr(new_product, attribute)
            )

    def test_updater_calls(self):
        SaveEdit(self.product_edit, self.user).save_edit()
        self.mock_CCAPI.create_product.assert_called_once_with(
            range_id=self.product_range.range_ID,
            name=self.product_range.name,
            description=self.product_range.description,
            barcode=self.product.barcode,
            vat_rate=0,
            sku=self.product.SKU,
        )
        self.mock_range_updater.set_department.assert_called_once_with(
            self.product_range.department
        )
        self.mock_range_updater.set_amazon_search_terms.assert_called_once_with(
            self.product_range.amazon_search_terms
        )
        self.mock_range_updater.set_amazon_bullet_points.assert_called_once_with(
            self.product_range.amazon_bullet_points
        )
        self.mock_product_updater.set_supplier.assert_called_once_with(
            self.product.supplier
        )
        self.mock_product_updater.set_supplier_SKU.assert_called_once_with(
            self.product.supplier_SKU
        )
        self.mock_product_updater.set_purchase_price.assert_called_once_with(
            self.product.purchase_price
        )
        self.mock_product_updater.set_VAT_rate.assert_called_once_with(
            self.product.VAT_rate
        )
        self.mock_product_updater.set_price.assert_called_once_with(self.product.price)
        self.mock_product_updater.set_retail_price.assert_called_once_with(
            self.product.retail_price
        )
        self.mock_product_updater.set_brand.assert_called_once_with(self.product.brand)
        self.mock_product_updater.set_manufacturer.assert_called_once_with(
            self.product.manufacturer
        )
        self.mock_product_updater.set_package_type.assert_called_once_with(
            self.product.package_type
        )
        self.mock_product_updater.set_international_shipping.assert_called_once_with(
            self.product.international_shipping
        )
        self.mock_product_updater.set_weight.assert_called_once_with(
            self.product.weight_grams
        )
        self.mock_product_updater.set_length.assert_called_once_with(
            self.product.length_mm
        )
        self.mock_product_updater.set_height.assert_called_once_with(
            self.product.height_mm
        )
        self.mock_product_updater.set_width.assert_called_once_with(
            self.product.width_mm
        )
        self.mock_product_updater.set_gender.assert_called_once_with(
            self.product.gender
        )
        self.mock_product_updater.set_bays.assert_called_once_with(
            list(self.product.bays.all())
        )
        self.mock_product_updater.set_date_created.assert_called_once()
        self.mock_product_updater.set_product_option_link.assert_has_calls(
            (
                call(self.small_product_option_value),
                call(self.red_product_option_value),
                call(self.model_product_option_value),
            )
        )
        self.assertEqual(
            3, len(self.mock_product_updater.set_product_option_link.mock_calls)
        )
        self.assertEqual(20, len(self.mock_product_updater.mock_calls))
        self.assertEqual(3, len(self.mock_range_updater.log.mock_calls))
        self.assertEqual(6, len(self.mock_range_updater.mock_calls))


# class TestSaveEditForNewRange(BaseSaveEditTest, fixtures.UnsavedNewProductRangeFixture):
#     fixtures = fixtures.UnsavedNewProductRangeFixture.fixtures
#
#     def setUp(self):
#         fixtures.UnsavedNewProductRangeFixture.setUp(self)
#         super().setUp()
