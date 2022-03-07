from decimal import Decimal
from unittest.mock import Mock, call, patch

from inventory import models
from inventory.cloud_commerce_updater import ProductUpdater, RangeUpdater, SaveEdit
from inventory.tests import fixtures
from stcadmin.tests.stcadmin_test import STCAdminTest


class BaseSaveEditTest:
    @classmethod
    def setUpTestData(cls):
        STCAdminTest.create_user()

    def setUp(self):
        self.setup_mocks()
        self.product_IDs = [_.product_ID for _ in self.product_range.products()]

    def setup_mocks(self):
        self.mock_CCAPI = Mock()
        range_ccapi_patcher = patch(
            "inventory.cloud_commerce_updater.range_updater.CCAPI", new=self.mock_CCAPI
        )
        product_ccapi_patcher = patch(
            "inventory.cloud_commerce_updater.product_updater.CCAPI",
            new=self.mock_CCAPI,
        )
        range_ccapi_patcher.start()
        product_ccapi_patcher.start()
        self.addCleanup(range_ccapi_patcher.stop)
        self.addCleanup(product_ccapi_patcher.stop)
        self.mock_CC_range = Mock()
        self.mock_CCAPI.get_range.return_value = self.mock_CC_range

    @property
    def partial_range(self):
        return models.PartialProductRange.objects.get(id=1)

    @property
    def original_range(self):
        return models.ProductRange.objects.get(id=1)

    @property
    def partial_product(self):
        return models.PartialProduct.objects.get(id=1)

    @property
    def original_product(self):
        return models.Product.objects.get(id=1)

    @property
    def partial_variations(self):
        return self.partial_range.products()

    @property
    def original_variations(self):
        return self.original_range.products()


class TestSaveEditForExistingRange(
    BaseSaveEditTest, STCAdminTest, fixtures.EditingProductFixture
):
    fixtures = fixtures.EditingProductFixture.fixtures

    def setUp(self):
        super().setUp()
        self.prepare_db()
        self.setup_mock_returns()
        self.make_edit()

    def prepare_db(self):
        pass

    def setup_mock_returns(self):
        pass

    def make_edit(self):
        self.save_edit = SaveEdit(self.product_edit, self.user)
        self.save_edit.save_edit()


class TestSaveEditForExistingRangeEdit(TestSaveEditForExistingRange):
    def test_save_edit(self):
        self.assertEqual(self.product_edit, self.save_edit.edit)
        self.assertEqual(self.user, self.save_edit.user)
        self.assertEqual(self.original_range, self.save_edit.original_range)
        self.assertEqual(self.product_range, self.save_edit.partial_range)
        self.assertEqual(0, len(self.mock_CCAPI.mock_calls))


class TestChangeRangeName(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_name = "New Range Name"
        self.assertNotEqual(self.new_name, self.original_range.name)
        partial_range = self.partial_range
        partial_range.name = self.new_name
        partial_range.save()

    def test_db_change(self):
        self.assertEqual(self.new_name, self.original_range.name)

    def test_cc_calls(self):
        self.mock_CCAPI.get_range.assert_called_once_with(self.partial_range.range_ID)
        self.mock_CC_range.set_name.assert_called_once_with(self.new_name)
        self.mock_CCAPI.set_product_name.assert_called_once_with(
            name=self.new_name, product_ids=self.product_IDs
        )
        self.assertEqual(3, len(self.mock_CCAPI.mock_calls))


class TestSetDepartment(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.assertNotEqual(self.second_department, self.original_range.department)
        partial_range = self.partial_range
        partial_range.department = self.second_department
        partial_range.save()

    def test_db_change(self):
        self.assertEqual(self.second_department, self.original_range.department)

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=self.product_IDs,
            option_id=models.Department.PRODUCT_OPTION_ID,
            option_value_id=self.second_department.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestSetDescription(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.description = "New Description\nFor the product range."
        self.assertNotEqual(self.description, self.original_range.description)
        partial_range = self.partial_range
        partial_range.description = self.description
        partial_range.save()

    def test_db_change(self):
        self.assertEqual(self.description, self.original_range.description)

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_description.assert_called_once_with(
            product_ids=self.product_IDs, description=self.description
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestChangeAmazonSearchTerms(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.search_terms = "mug|cup"
        self.assertNotEqual(self.search_terms, self.original_range.amazon_search_terms)
        partial_range = self.partial_range
        partial_range.amazon_search_terms = self.search_terms
        partial_range.save()

    def setup_mock_returns(self):
        self.product_option_value_ID = "284938"
        self.mock_CCAPI.get_option_value_id.return_value = self.product_option_value_ID

    def test_db_change(self):
        self.assertEqual(self.search_terms, self.original_range.amazon_search_terms)

    def test_cc_calls(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=RangeUpdater.AMAZON_SEARCH_TERMS_OPTION_ID,
            value=self.search_terms,
            create=True,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=self.product_IDs,
            option_id=RangeUpdater.AMAZON_SEARCH_TERMS_OPTION_ID,
            option_value_id=self.product_option_value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestChangeAmzonBulletPoints(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.bullets = "mug|cup"
        self.assertNotEqual(self.bullets, self.original_range.amazon_bullet_points)
        partial_range = self.partial_range
        partial_range.amazon_bullet_points = self.bullets
        partial_range.save()

    def setup_mock_returns(self):
        self.product_option_value_ID = "284938"
        self.mock_CCAPI.get_option_value_id.return_value = self.product_option_value_ID

    def test_db_change(self):
        self.assertEqual(self.bullets, self.original_range.amazon_bullet_points)

    def test_cc_calls(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=RangeUpdater.AMAZON_BULLET_POINTS_OPTION_ID,
            value=self.bullets,
            create=True,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=self.product_IDs,
            option_id=RangeUpdater.AMAZON_BULLET_POINTS_OPTION_ID,
            option_value_id=self.product_option_value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestChangeSupplier(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_supplier = self.second_supplier
        self.assertNotEqual(self.new_supplier, self.original_product.supplier)
        partial_product = self.partial_product
        partial_product.supplier = self.new_supplier
        partial_product.save()

    def setup_mock_returns(self):
        self.mock_links = [Mock(link_id="829304"), Mock(link_id="384932")]
        self.mock_CCAPI.get_product_factory_links.return_value = self.mock_links

    def test_db_change(self):
        self.assertEqual(self.new_supplier, self.original_product.supplier)

    def test_cc_calls(self):
        self.mock_CCAPI.get_product_factory_links.assert_called_once_with(
            self.product.product_ID
        )
        for link in self.mock_links:
            self.mock_CCAPI.delete_product_factory_link.assert_any_call(link.link_id)
        self.assertEqual(2, len(self.mock_CCAPI.delete_product_factory_link.mock_calls))
        self.mock_CCAPI.update_product_factory_link.assert_called_once_with(
            product_id=self.partial_product.product_ID,
            factory_id=self.new_supplier.factory_ID,
            dropship=False,
            supplier_sku=self.partial_product.supplier_SKU,
            price=self.partial_product.purchase_price,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=models.Supplier.PRODUCT_OPTION_ID,
            option_value_id=self.new_supplier.product_option_value_ID,
        )
        self.assertEqual(5, len(self.mock_CCAPI.mock_calls))


class TestChangeSupplierSKU(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_supplier_SKU = "BN0383"
        self.assertNotEqual(self.new_supplier_SKU, self.original_product.supplier_SKU)
        partial_product = self.partial_product
        partial_product.supplier_SKU = self.new_supplier_SKU
        partial_product.save()

    def setup_mock_returns(self):
        self.option_ID = ProductUpdater.SUPPLIER_SKU_PRODUCT_OPTION_ID
        self.product_option_value_ID = "6546156"
        self.mock_CCAPI.get_option_value_id.return_value = self.product_option_value_ID

    def test_db_change(self):
        self.assertEqual(self.new_supplier_SKU, self.original_product.supplier_SKU)

    def test_cc_calls(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=self.new_supplier_SKU, create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.product_option_value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestChangeBarcode(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_barcode = "0387547393"
        self.assertNotEqual(self.original_product.barcode, self.new_barcode)
        partial_product = self.partial_product
        partial_product.barcode = self.new_barcode
        partial_product.save()

    def test_db_change(self):
        self.assertEqual(self.new_barcode, self.original_product.barcode)

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_barcode.assert_called_once_with(
            product_id=self.partial_product.product_ID, barcode=self.new_barcode
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestChangePurchasePrice(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_purchase_price = "5.99"
        self.assertNotEqual(
            self.original_product.purchase_price, Decimal(self.new_purchase_price)
        )
        partial_product = self.partial_product
        partial_product.purchase_price = self.new_purchase_price
        partial_product.save()

    def setup_mock_returns(self):
        self.option_ID = ProductUpdater.PURCHASE_PRICE_PRODUCT_OPTION_ID
        self.value_ID = "2849829"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID

    def test_db_change(self):
        self.assertEqual(
            Decimal(self.new_purchase_price), self.original_product.purchase_price
        )

    def test_cc_calls(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=self.new_purchase_price, create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestChangeVATRate(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_VAT_rate = self.second_VAT_rate
        self.assertNotEqual(self.new_VAT_rate, self.original_product.VAT_rate)
        partial_product = self.partial_product
        partial_product.VAT_rate = self.new_VAT_rate
        partial_product.save()

    def test_db_change(self):
        self.assertEqual(self.new_VAT_rate, self.original_product.VAT_rate)

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_vat_rate_by_id.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            vat_rate_id=self.new_VAT_rate.VAT_rate_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestChangePrice(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_price = "8.74"
        self.assertNotEqual(Decimal(self.new_price), self.original_product.price)
        partial_product = self.partial_product
        partial_product.price = self.new_price
        partial_product.save()

    def test_db_change(self):
        self.assertEqual(Decimal(self.new_price), self.original_product.price)

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_base_price.assert_called_once_with(
            product_id=self.partial_product.product_ID, price=self.new_price
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestChangeRetailPrice(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_price = "8.74"
        self.assertNotEqual(Decimal(self.new_price), self.original_product.retail_price)
        partial_product = self.partial_product
        partial_product.retail_price = self.new_price
        partial_product.save()

    def setup_mock_returns(self):
        self.option_ID = ProductUpdater.RETAIL_PRICE_PRODUCT_OPTION_ID
        self.value_ID = "94651564"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID

    def test_db_change(self):
        self.assertEqual(Decimal(self.new_price), self.original_product.retail_price)

    def test_cc_calls(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=self.new_price, create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestChangeBrand(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_brand = self.second_brand
        self.assertNotEqual(self.new_brand, self.original_product.brand)
        partial_product = self.partial_product
        partial_product.brand = self.new_brand
        partial_product.save()

    def test_db_change(self):
        self.assertEqual(self.new_brand, self.original_product.brand)

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=self.new_brand.PRODUCT_OPTION_ID,
            option_value_id=self.new_brand.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestChangeManufacturer(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_manufacturer = self.second_manufacturer
        self.assertNotEqual(self.new_manufacturer, self.original_product.manufacturer)
        partial_product = self.partial_product
        partial_product.manufacturer = self.new_manufacturer
        partial_product.save()

    def test_db_change(self):
        self.assertEqual(self.new_manufacturer, self.original_product.manufacturer)

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=self.new_manufacturer.PRODUCT_OPTION_ID,
            option_value_id=self.new_manufacturer.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestChangePackageType(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.new_package_type = self.second_package_type
        self.assertNotEqual(self.new_package_type, self.original_product.package_type)
        partial_product = self.partial_product
        partial_product.package_type = self.new_package_type
        partial_product.save()

    def test_db_change(self):
        self.assertEqual(self.new_package_type, self.original_product.package_type)

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=self.new_package_type.PRODUCT_OPTION_ID,
            option_value_id=self.new_package_type.product_option_value_ID,
        )
        self.mock_CCAPI.set_product_scope.assert_called_once_with(
            product_id=self.partial_product.product_ID,
            weight=self.partial_product.weight_grams,
            height=0,
            length=0,
            width=0,
            large_letter_compatible=self.new_package_type.large_letter_compatible,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestChangeInternationalShipping(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.assertNotEqual(
            self.second_international_shipping,
            self.original_product.international_shipping,
        )
        partial_product = self.partial_product
        partial_product.international_shipping = self.second_international_shipping
        partial_product.save()

    def test_db_change(self):
        self.assertEqual(
            self.second_international_shipping,
            self.original_product.international_shipping,
        )

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=self.second_international_shipping.PRODUCT_OPTION_ID,
            option_value_id=self.second_international_shipping.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestChangeWeight(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.weight = 584
        self.assertNotEqual(self.weight, self.original_product.weight_grams)
        partial_product = self.partial_product
        partial_product.weight_grams = self.weight
        partial_product.save()

    def test_db_change(self):
        self.assertEqual(self.weight, self.original_product.weight_grams)

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_scope.assert_called_once_with(
            product_id=self.partial_product.product_ID,
            weight=self.weight,
            height=0,
            length=0,
            width=0,
            large_letter_compatible=self.partial_product.package_type.large_letter_compatible,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestChangeLength(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.length = 1150
        self.assertNotEqual(self.length, self.original_product.length_mm)
        partial_product = self.partial_product
        partial_product.length_mm = self.length
        partial_product.save()

    def setup_mock_returns(self):
        self.option_ID = ProductUpdater.LENGTH_PRODUCT_OPTION_ID
        self.value_ID = "9816156"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID

    def test_db_change(self):
        self.assertEqual(self.length, self.original_product.length_mm)

    def test_cc_calls(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=str(self.length), create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestChangeWidth(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.width = 860
        self.assertNotEqual(self.width, self.original_product.width_mm)
        partial_product = self.partial_product
        partial_product.width_mm = self.width
        partial_product.save()

    def setup_mock_returns(self):
        self.option_ID = ProductUpdater.WIDTH_PRODUCT_OPTION_ID
        self.value_ID = "1324864"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID

    def test_db_change(self):
        self.assertEqual(self.width, self.original_product.width_mm)

    def test_cc_calls(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=str(self.width), create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestChangeHeight(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.height = 1150
        self.assertNotEqual(self.height, self.original_product.height_mm)
        partial_product = self.partial_product
        partial_product.height_mm = self.height
        partial_product.save()

    def setup_mock_returns(self):
        self.option_ID = ProductUpdater.HEIGHT_PRODUCT_OPTION_ID
        self.value_ID = "9816156"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID

    def test_db_change(self):
        self.assertEqual(self.height, self.original_product.height_mm)

    def test_cc_calls(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=str(self.height), create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestChangeGender(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.assertNotEqual(self.second_gender, self.original_product.gender)
        partial_product = self.partial_product
        partial_product.gender = self.second_gender
        partial_product.save()

    def test_db_change(self):
        self.assertEqual(self.second_gender, self.original_product.gender)

    def test_cc_calls(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.partial_product.product_ID],
            option_id=self.second_gender.PRODUCT_OPTION_ID,
            option_value_id=self.second_gender.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestChangeBays(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.original_bays = list(self.original_product.bays.all().order_by("name"))
        self.new_bays = [self.warehouse_2_bay_1, self.warehouse_2_bay_2]

    def setup_mock_returns(self):
        mock_existing_bays = [Mock(id=bay.bay_ID) for bay in self.original_bays]
        self.mock_CCAPI.get_bays_for_product.return_value = mock_existing_bays
        self.assertNotEqual(self.new_bays, self.original_bays)
        self.partial_product.bays.set(self.new_bays)

    def test_db_change(self):
        self.assertCountEqual(self.new_bays, list(self.product.bays.all()))

    def test_cc_calls(self):
        self.mock_CCAPI.get_bays_for_product.assert_called_once_with(
            self.partial_product.product_ID
        )
        remove_bay_calls = [
            call(self.partial_product.product_ID, bay.bay_ID)
            for bay in self.original_bays
        ]
        self.mock_CCAPI.remove_warehouse_bay_from_product.assert_has_calls(
            remove_bay_calls
        )
        self.assertEqual(
            3, len(self.mock_CCAPI.remove_warehouse_bay_from_product.mock_calls)
        )
        self.mock_CCAPI.add_warehouse_bay_to_product.assert_has_calls(
            [call(self.partial_product.product_ID, bay.bay_ID) for bay in self.new_bays]
        )
        self.assertEqual(
            2, len(self.mock_CCAPI.add_warehouse_bay_to_product.mock_calls)
        )
        self.assertEqual(6, len(self.mock_CCAPI.mock_calls))


class TestChangeProductOptionLinks(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.old_option_value = self.small_product_option_value
        self.new_option_value = self.xl_product_option_value
        self.assertTrue(
            models.ProductOptionValueLink.objects.filter(
                product=self.original_product,
                product_option_value=self.old_option_value,
            ).exists()
        )
        self.assertFalse(
            models.ProductOptionValueLink.objects.filter(
                product=self.original_product,
                product_option_value=self.new_option_value,
            )
        )
        models.PartialProductOptionValueLink.objects.get(
            product=self.partial_product, product_option_value=self.old_option_value
        ).delete()
        models.PartialProductOptionValueLink.objects.create(
            product=self.partial_product, product_option_value=self.new_option_value
        )

    def test_db_change(self):
        self.assertFalse(
            models.ProductOptionValueLink.objects.filter(
                product=self.original_product,
                product_option_value=self.old_option_value,
            ).exists()
        )
        self.assertTrue(
            models.ProductOptionValueLink.objects.filter(
                product=self.original_product,
                product_option_value=self.new_option_value,
            )
        )

    def test_cc_calls(self):
        calls = [
            call(
                product_ids=[self.original_product.product_ID],
                option_id=self.old_option_value.product_option.product_option_ID,
                option_value_id=0,
            ),
            call(
                product_ids=[self.original_product.product_ID],
                option_id=self.new_option_value.product_option.product_option_ID,
                option_value_id=self.new_option_value.product_option_value_ID,
            ),
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(calls)
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestAddListingOptionToExistingProduct(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.product_option = self.design_product_option
        self.product_option_value = self.cat_product_option_value
        models.PartialProductRangeSelectedOption.objects.create(
            product_range=self.partial_range,
            product_option=self.product_option,
            variation=False,
        )
        models.PartialProductOptionValueLink.objects.create(
            product=self.partial_product, product_option_value=self.product_option_value
        )

    def test_db_change(self):
        self.assertTrue(
            models.ProductRangeSelectedOption.objects.filter(
                product_range=self.original_range,
                product_option=self.product_option,
                variation=False,
            ).exists()
        )
        self.assertTrue(
            models.ProductOptionValueLink.objects.filter(
                product=self.original_product,
                product_option_value=self.product_option_value,
            ).exists()
        )

    def test_cc_calls(self):
        self.mock_CCAPI.add_option_to_product.assert_called_once_with(
            range_id=self.original_range.range_ID,
            option_id=self.product_option.product_option_ID,
        )
        self.mock_CCAPI.set_range_option_drop_down.assert_called_once_with(
            range_id=self.original_range.range_ID,
            option_id=self.product_option.product_option_ID,
            drop_down=False,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.original_product.product_ID],
            option_id=self.product_option.product_option_ID,
            option_value_id=self.product_option_value.product_option_value_ID,
        )
        self.assertEqual(3, len(self.mock_CCAPI.mock_calls))


class TestAddVariationOptionToExistingProduct(TestSaveEditForExistingRange):
    def prepare_db(self):
        self.product_option = self.design_product_option
        self.product_option_value = self.cat_product_option_value
        models.PartialProductRangeSelectedOption.objects.create(
            product_range=self.partial_range,
            product_option=self.product_option,
            variation=True,
        )
        models.PartialProductOptionValueLink.objects.create(
            product=self.partial_product, product_option_value=self.product_option_value
        )

    def test_db_change(self):
        self.assertTrue(
            models.ProductRangeSelectedOption.objects.filter(
                product_range=self.original_range,
                product_option=self.product_option,
                variation=True,
            ).exists()
        )
        self.assertTrue(
            models.ProductOptionValueLink.objects.filter(
                product=self.original_product,
                product_option_value=self.product_option_value,
            ).exists()
        )

    def test_cc_calls(self):
        self.mock_CCAPI.add_option_to_product.assert_called_once_with(
            range_id=self.original_range.range_ID,
            option_id=self.product_option.product_option_ID,
        )
        self.mock_CCAPI.set_range_option_drop_down.assert_called_once_with(
            range_id=self.original_range.range_ID,
            option_id=self.product_option.product_option_ID,
            drop_down=True,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.original_product.product_ID],
            option_id=self.product_option.product_option_ID,
            option_value_id=self.product_option_value.product_option_value_ID,
        )
        self.assertEqual(3, len(self.mock_CCAPI.mock_calls))


class TestRemoveProductOptionFromExistingRange(TestSaveEditForExistingRange):
    def prepare_db(self):
        models.PartialProductOptionValueLink.objects.filter(
            product__product_range=self.partial_range,
            product_option_value__product_option=self.model_product_option,
        ).delete()
        models.PartialProductRangeSelectedOption.objects.filter(
            product_range=self.partial_range, product_option=self.model_product_option
        ).delete()

    def test_db_changes(self):
        link_query = models.ProductOptionValueLink.objects.filter(
            product__product_range=self.original_range,
            product_option_value__product_option=self.model_product_option,
        ).exists()
        self.assertFalse(link_query)
        selected_query = models.ProductRangeSelectedOption.objects.filter(
            product_range=self.original_range, product_option=self.model_product_option
        ).exists()
        self.assertFalse(selected_query)

    def test_cc_calls(self):
        self.mock_CCAPI.remove_option_from_product.assert_called_once_with(
            range_id=self.original_range.range_ID,
            option_id=self.model_product_option.product_option_ID,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=self.product_IDs,
            option_id=self.model_product_option.product_option_ID,
            option_value_id=0,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestSaveEditWithNewVariation(
    BaseSaveEditTest, STCAdminTest, fixtures.EditingProductFixture
):
    fixtures = fixtures.EditingProductFixture.fixtures

    @classmethod
    def setUpTestData(cls):
        STCAdminTest.create_user()
        models.Product.objects.get(id=1).delete()

    def setUp(self):
        partial_product = self.partial_product
        self.partial_product_SKU = partial_product.SKU
        partial_product.pre_existing = False
        partial_product.barcode = "385493829"
        self.setup_mocks()
        partial_product.save()

    def setup_mocks(self):
        super().setup_mocks()
        self.new_product_ID = "2849382"
        self.mock_CCAPI.create_product.return_value = self.new_product_ID
        self.mock_CCAPI.get_product_factory_links.return_value = []
        self.mock_CCAPI.get_bays_for_product.return_value = [
            Mock(bay_id=bay.bay_ID) for bay in self.partial_product.bays.all()
        ]

    def test_new_database_product(self):
        SaveEdit(self.product_edit, self.user).save_edit()
        new_product = models.Product.objects.get(SKU=self.partial_product_SKU)
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
        new_product = models.Product.objects.get(SKU=self.partial_product_SKU)
        variation_count = 1
        range_option_IDs_to_get = 2
        product_option_IDs_to_get = 7
        get_option_value_calls = (
            product_option_IDs_to_get * variation_count
        ) + range_option_IDs_to_get
        product_options_to_set = 16
        range_options_to_set = 3
        set_product_option_value_calls = (
            product_options_to_set * variation_count
        ) + range_options_to_set
        expected_calls = {
            "create_range": 0,
            "create_product": variation_count,
            "set_product_name": 0,
            "set_product_description": 0,
            "remove_option_from_product": 0,
            "add_option_to_product": 0,
            "set_range_option_drop_down": 0,
            "create_product": variation_count,
            "set_product_base_price": variation_count,
            "get_option_value_id": get_option_value_calls,
            "set_product_option_value": set_product_option_value_calls,
            "get_product_factory_links": variation_count,
            "update_product_factory_link": variation_count,
            "set_product_vat_rate_by_id": variation_count,
            "set_product_scope": variation_count * 2,
            "set_product_barcode": 0,
            "get_bays_for_product": variation_count,
            "remove_warehouse_bay_from_product": 3,
            "add_warehouse_bay_to_product": new_product.bays.all().count(),
            "get_range": 0,
            "get_product": 0,
        }
        total_expected_calls = 0
        for method_name, call_count in expected_calls.items():
            total_expected_calls += call_count
            mock_method = getattr(self.mock_CCAPI, method_name)
            actual_call_count = len(mock_method.mock_calls)
            self.assertEqual(
                call_count,
                actual_call_count,
                (
                    f"Expected {call_count} calls for the {method_name} method, "
                    f"found {actual_call_count}",
                ),
            )
        total_calls = len(self.mock_CCAPI.mock_calls)
        self.assertEqual(
            total_expected_calls,
            total_calls,
            (f"Expected {total_expected_calls} CCAPI calls, found {total_calls}."),
        )


class TestSaveEditForNewRange(
    BaseSaveEditTest, STCAdminTest, fixtures.UnsavedNewProductRangeFixture
):
    fixtures = fixtures.UnsavedNewProductRangeFixture.fixtures

    product_option_value_IDs = {
        (ProductUpdater.SUPPLIER_SKU_PRODUCT_OPTION_ID, "TV009"): "8994616",
        (ProductUpdater.PURCHASE_PRICE_PRODUCT_OPTION_ID, "5.60"): "9816515",
        (ProductUpdater.RETAIL_PRICE_PRODUCT_OPTION_ID, "12.70"): "8916645",
        (ProductUpdater.LENGTH_PRODUCT_OPTION_ID, "50"): "3993829",
        (ProductUpdater.HEIGHT_PRODUCT_OPTION_ID, "150"): "9484939",
        (ProductUpdater.WIDTH_PRODUCT_OPTION_ID, "24"): "3849392",
    }

    @property
    def new_range(self):
        return models.ProductRange.objects.get(SKU=self.partial_range.SKU)

    @property
    def new_product(self):
        return models.Product.objects.get(SKU=self.product.SKU)

    @property
    def new_variations(self):
        return self.new_range.products()

    def setup_mocks(self):
        super().setup_mocks()
        self.new_range_ID = "8493833"
        self.new_product_IDs = [
            "2849382",
            "8487349",
            "4783894",
            "9384983",
            "7468974",
            "8694162",
            "1596466",
            "9461566",
            "8946168",
        ]
        self.mock_CCAPI.create_product.side_effect = self.new_product_IDs
        self.mock_CCAPI.create_range.return_value = self.new_range_ID
        self.mock_factory_links = []
        self.mock_CCAPI.get_product_factory_links.return_value = self.mock_factory_links
        self.mock_CCAPI.get_bays_for_product.return_value = []
        self.mock_CCAPI.get_option_value_id.side_effect = (
            self.get_option_value_id_side_effect
        )
        SaveEdit(self.product_edit, self.user).save_edit()

    def get_option_value_id_side_effect(self, *args, **kwargs):
        option_ID = kwargs.get("option_id")
        if option_ID == ProductUpdater.DATE_CREATED_PRODUCT_OPTION_ID:
            return "2849332"
        value = kwargs.get("value")
        return self.product_option_value_IDs.get((option_ID, value))

    def test_new_range(self):
        self.assertEqual(
            1, models.ProductRange.objects.filter(SKU=self.product_range.SKU).count()
        )
        new_range = models.ProductRange.objects.get(SKU=self.product_range.SKU)
        self.assertEqual(self.new_range_ID, new_range.range_ID)
        self.assertEqual(self.product_range.name, new_range.name)

    def test_new_database_products(self):
        for i, partial_product in enumerate(self.partial_variations):
            new_product = models.Product.objects.get(SKU=partial_product.SKU)
            new_product_range = models.ProductRange.objects.get(
                SKU=self.product_range.SKU
            )
            self.assertEqual(new_product.product_range, new_product_range)
            self.assertEqual(self.new_product_IDs[i], new_product.product_ID)
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
                    getattr(partial_product, attribute), getattr(new_product, attribute)
                )

    def test_new_range_created_in_database(self):
        partial_range = self.partial_range
        self.assertTrue(
            models.ProductRange.objects.filter(SKU=partial_range.SKU).exists()
        )
        new_range = models.ProductRange.objects.get(SKU=partial_range.SKU)
        self.assertEqual(self.new_range_ID, new_range.range_ID)
        self.assertEqual(partial_range.name, new_range.name)
        self.assertEqual(partial_range.department, new_range.department)
        self.assertEqual(partial_range.description, new_range.description)
        self.assertEqual(
            partial_range.amazon_search_terms, new_range.amazon_search_terms
        )
        self.assertEqual(
            partial_range.amazon_bullet_points, new_range.amazon_bullet_points
        )
        self.assertTrue(
            models.ProductRangeSelectedOption.objects.filter(
                product_range=new_range,
                product_option=self.model_product_option,
                variation=False,
            ).exists()
        )
        variation_options = (self.size_product_option, self.colour_product_option)
        for option in variation_options:
            self.assertTrue(
                models.ProductRangeSelectedOption.objects.filter(
                    product_range=new_range, product_option=option, variation=True
                ).exists()
            )

    def test_new_range_created_in_cloud_commerce(self):
        self.mock_CCAPI.create_range.assert_called_once_with(
            range_name=self.product_range.name, sku=self.product_range.SKU
        )
        self.mock_CCAPI.get_range.assert_called_once_with(self.new_range_ID)

    def test_create_product_calls(self):
        new_range = models.ProductRange.objects.get(SKU=self.product_range.SKU)
        create_product_calls = [
            call(
                range_id=new_range.range_ID,
                name=new_range.name,
                description=new_range.description,
                barcode=product.barcode,
                vat_rate=0,
                sku=product.SKU,
            )
            for product in self.new_variations
        ]
        self.mock_CCAPI.create_product.assert_has_calls(create_product_calls)
        self.assertEqual(9, len(self.mock_CCAPI.create_product.mock_calls))

    def test_set_supplier_calls(self):
        remove_factory_link_calls = [
            call(link.link_id) for link in self.mock_factory_links
        ] * 9
        self.mock_CCAPI.delete_product_factory_link.assert_has_calls(
            remove_factory_link_calls
        )
        self.assertEqual(0, len(self.mock_CCAPI.delete_product_factory_link.mock_calls))
        update_factory_link_calls = [
            call(
                product_id=product.product_ID,
                factory_id=self.supplier.factory_ID,
                dropship=False,
                supplier_sku=product.supplier_SKU,
                price=product.purchase_price,
            )
            for product in self.new_variations
        ]
        self.mock_CCAPI.update_product_factory_link.assert_has_calls(
            update_factory_link_calls
        )
        self.assertEqual(9, len(self.mock_CCAPI.update_product_factory_link.mock_calls))
        set_product_option_value_calls = [
            call(
                product_ids=[product.product_ID],
                option_id=models.Supplier.PRODUCT_OPTION_ID,
                option_value_id=self.supplier.product_option_value_ID,
            )
            for product in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(
            set_product_option_value_calls, any_order=True
        )

    def test_set_supplier_SKU_calls(self):
        option_ID = ProductUpdater.SUPPLIER_SKU_PRODUCT_OPTION_ID
        get_option_value_id_calls = [
            call(option_id=option_ID, value=variation.supplier_SKU, create=True)
            for variation in self.new_variations
        ]
        self.mock_CCAPI.get_option_value_id.assert_has_calls(
            get_option_value_id_calls, any_order=True
        )
        create_option_value_calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=option_ID,
                option_value_id=self.product_option_value_IDs[
                    (option_ID, variation.supplier_SKU)
                ],
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(
            create_option_value_calls, any_order=True
        )

    def test_set_purchase_price(self):
        option_ID = ProductUpdater.PURCHASE_PRICE_PRODUCT_OPTION_ID
        get_option_value_calls = [
            call(
                option_id=option_ID,
                value="{:.2f}".format(float(variation.purchase_price)),
                create=True,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.get_option_value_id.assert_has_calls(
            get_option_value_calls, any_order=True
        )
        set_option_value_calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=option_ID,
                option_value_id=self.product_option_value_IDs[(option_ID, "5.60")],
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(
            set_option_value_calls, any_order=True
        )

    def test_set_VAT_rate_calls(self):
        calls = [
            call(
                product_ids=[variation.product_ID],
                vat_rate_id=variation.VAT_rate.VAT_rate_ID,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_vat_rate_by_id.assert_has_calls(
            calls, any_order=True
        )

    def test_set_price_calls(self):
        calls = [
            call(
                product_id=variation.product_ID,
                price="{:.2f}".format(float(variation.price)),
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_base_price.assert_has_calls(calls, any_order=True)

    def test_set_retail_price_calls(self):
        option_ID = ProductUpdater.RETAIL_PRICE_PRODUCT_OPTION_ID
        get_option_value_calls = [
            call(
                option_id=option_ID,
                value="{:.2f}".format(float(variation.retail_price)),
                create=True,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.get_option_value_id.assert_has_calls(
            get_option_value_calls, any_order=True
        )
        set_option_value_calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=option_ID,
                option_value_id=self.product_option_value_IDs[
                    (option_ID, "{:.2f}".format(float(variation.retail_price)))
                ],
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(
            set_option_value_calls, any_order=True
        )

    def test_set_brand_calls(self):
        calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=variation.brand.PRODUCT_OPTION_ID,
                option_value_id=variation.brand.product_option_value_ID,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(calls, any_order=True)

    def test_set_manufacturer_calls(self):
        calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=variation.manufacturer.PRODUCT_OPTION_ID,
                option_value_id=variation.manufacturer.product_option_value_ID,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(calls, any_order=True)

    def test_set_package_type_calls(self):
        set_option_calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=variation.package_type.PRODUCT_OPTION_ID,
                option_value_id=variation.package_type.product_option_value_ID,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(
            set_option_calls, any_order=True
        )
        product_scope_calls = [
            call(
                product_id=variation.product_ID,
                weight=variation.weight_grams,
                height=0,
                length=0,
                width=0,
                large_letter_compatible=variation.package_type.large_letter_compatible,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_scope.assert_has_calls(
            product_scope_calls, any_order=True
        )

    def test_set_international_shipping_calls(self):
        calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=variation.international_shipping.PRODUCT_OPTION_ID,
                option_value_id=variation.international_shipping.product_option_value_ID,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(calls, any_order=True)

    def test_set_weight_calls(self):
        calls = [
            call(
                product_id=variation.product_ID,
                weight=variation.weight_grams,
                height=0,
                length=0,
                width=0,
                large_letter_compatible=variation.package_type.large_letter_compatible,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_scope.assert_has_calls(calls, any_order=True)

    def test_set_length_calls(self):
        option_ID = ProductUpdater.LENGTH_PRODUCT_OPTION_ID
        get_option_value_calls = [
            call(option_id=option_ID, value=str(variation.length_mm), create=True)
            for variation in self.new_variations
        ]
        self.mock_CCAPI.get_option_value_id.assert_has_calls(
            get_option_value_calls, any_order=True
        )
        set_option_value_calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=option_ID,
                option_value_id=self.product_option_value_IDs[
                    (option_ID, str(variation.length_mm))
                ],
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(
            set_option_value_calls, any_order=True
        )

    def test_set_height_calls(self):
        option_ID = ProductUpdater.HEIGHT_PRODUCT_OPTION_ID
        get_option_value_calls = [
            call(option_id=option_ID, value=str(variation.height_mm), create=True)
            for variation in self.new_variations
        ]
        self.mock_CCAPI.get_option_value_id.assert_has_calls(
            get_option_value_calls, any_order=True
        )
        set_option_value_calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=option_ID,
                option_value_id=self.product_option_value_IDs[
                    (option_ID, str(variation.height_mm))
                ],
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(
            set_option_value_calls, any_order=True
        )

    def test_set_width_calls(self):
        option_ID = ProductUpdater.WIDTH_PRODUCT_OPTION_ID
        get_option_value_calls = [
            call(option_id=option_ID, value=str(variation.width_mm), create=True)
            for variation in self.new_variations
        ]
        self.mock_CCAPI.get_option_value_id.assert_has_calls(
            get_option_value_calls, any_order=True
        )
        set_option_value_calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=option_ID,
                option_value_id=self.product_option_value_IDs[
                    (option_ID, str(variation.width_mm))
                ],
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(
            set_option_value_calls, any_order=True
        )

    def test_set_gender_calls(self):
        calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=variation.gender.PRODUCT_OPTION_ID,
                option_value_id=variation.gender.product_option_value_ID,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(calls, any_order=True)

    def test_set_bays_calls(self):
        for variation in self.new_variations:
            for bay in variation.bays.all():
                self.mock_CCAPI.add_warehouse_bay_to_product.assert_has_calls(
                    [call(variation.product_ID, bay.bay_ID)], any_order=True
                )

    def test_set_date_created_calls(self):
        option_ID = ProductUpdater.DATE_CREATED_PRODUCT_OPTION_ID
        get_option_value_calls = [
            call(
                option_id=option_ID,
                value=variation.date_created.strftime("%Y-%m-%d"),
                create=True,
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.get_option_value_id.assert_has_calls(
            get_option_value_calls, any_order=True
        )
        set_option_value_calls = [
            call(
                product_ids=[variation.product_ID],
                option_id=option_ID,
                option_value_id=self.get_option_value_id_side_effect(
                    option_id=option_ID
                ),
            )
            for variation in self.new_variations
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(
            set_option_value_calls, any_order=True
        )

    def test_set_product_option_link_calls(self):
        links = models.ProductOptionValueLink.objects.filter(
            product__product_range=self.new_range
        )
        calls = [
            call(
                product_ids=[link.product.product_ID],
                option_id=link.product_option_value.product_option.product_option_ID,
                option_value_id=link.product_option_value.product_option_value_ID,
            )
            for link in links
        ]
        self.mock_CCAPI.set_product_option_value.assert_has_calls(calls, any_order=True)

    def test_call_counts(self):
        variation_count = len(self.new_variations)
        range_option_IDs_to_get = 2
        product_option_IDs_to_get = 7
        get_option_value_calls = (
            product_option_IDs_to_get * variation_count
        ) + range_option_IDs_to_get
        product_options_to_set = 16
        range_options_to_set = 3
        set_product_option_value_calls = (
            product_options_to_set * variation_count
        ) + range_options_to_set
        expected_calls = {
            "create_range": 1,
            "create_product": variation_count,
            "set_product_name": 0,
            "set_product_description": 0,
            "remove_option_from_product": 0,
            "add_option_to_product": 3,
            "set_range_option_drop_down": 3,
            "create_product": variation_count,
            "set_product_base_price": variation_count,
            "get_option_value_id": get_option_value_calls,
            "set_product_option_value": set_product_option_value_calls,
            "get_product_factory_links": variation_count,
            "update_product_factory_link": variation_count,
            "set_product_vat_rate_by_id": variation_count,
            "set_product_scope": variation_count * 2,
            "set_product_barcode": 0,
            "get_bays_for_product": variation_count,
            "remove_warehouse_bay_from_product": 0,
            "add_warehouse_bay_to_product": sum(
                [variation.bays.all().count() for variation in self.new_variations]
            ),
            "get_range": 1,
            "get_product": 0,
        }
        total_expected_calls = 0
        for method_name, call_count in expected_calls.items():
            total_expected_calls += call_count
            mock_method = getattr(self.mock_CCAPI, method_name)
            actual_call_count = len(mock_method.mock_calls)
            self.assertEqual(
                call_count,
                actual_call_count,
                (
                    f"Expected {call_count} calls for the {method_name} method, "
                    f"found {actual_call_count}",
                ),
            )
        total_calls = len(self.mock_CCAPI.mock_calls)
        self.assertEqual(
            total_expected_calls,
            total_calls,
            (f"Expected {total_expected_calls} CCAPI calls, found {total_calls}."),
        )
