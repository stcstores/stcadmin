from decimal import Decimal
from unittest.mock import Mock, call

from inventory import models
from inventory.cloud_commerce_updater import PartialProductUpdater, ProductUpdater
from inventory.tests import fixtures

from .test_updater_base import BaseUpdaterMethodTest, BaseUpdaterTest


class BaseProductUpdaterTest(BaseUpdaterTest):
    patch_path = "inventory.cloud_commerce_updater.product_updater.CCAPI"

    def updater_object(self):
        return self.product


class ProductUpdaterTest(BaseProductUpdaterTest, fixtures.VariationProductRangeFixture):
    updater_class = ProductUpdater

    def test_update_DB(self):
        self.update_DB_test()

    def test_update_CC(self):
        self.update_CC_test()


class PartialProductUpdaterTest(BaseProductUpdaterTest, fixtures.EditingProductFixture):
    updater_class = PartialProductUpdater

    def test_update_DB(self):
        self.update_DB_test()

    def test_update_CC(self):
        self.no_CC_update_test()


class NoChangeProductUpdaterTest(
    BaseProductUpdaterTest, fixtures.VariationProductRangeFixture
):
    updater_class = ProductUpdater

    def update_updater(self):
        self.updater.update_DB = False
        self.updater.update_CC = False

    def test_update_DB(self):
        self.no_DB_update_test()

    def test_update_CC(self):
        self.no_CC_update_test()


class TestSetSupplier(BaseUpdaterMethodTest):
    def setup_test(self):
        self.mock_links = [Mock(link_id="829304"), Mock(link_id="384932")]
        self.mock_CCAPI.get_product_factory_links.return_value = self.mock_links
        self.original_supplier = self.product.supplier
        self.new_supplier = models.Supplier.objects.create(
            name="New Supplier",
            product_option_value_ID="23840938",
            factory_ID="34854392",
        )
        self.updater.set_supplier(self.new_supplier)

    def update_DB_test(self):
        self.assertEqual(self.new_supplier, self.product.supplier)

    def no_DB_update_test(self):
        self.assertEqual(self.original_supplier, self.product.supplier)

    def update_CC_test(self):
        self.mock_CCAPI.get_product_factory_links.assert_called_once_with(
            self.product.product_ID
        )
        for link in self.mock_links:
            self.mock_CCAPI.delete_product_factory_link.assert_any_call(link.link_id)
        self.assertEqual(2, len(self.mock_CCAPI.delete_product_factory_link.mock_calls))
        self.mock_CCAPI.update_product_factory_link.assert_called_once_with(
            product_id=self.product.product_ID,
            factory_id=self.new_supplier.factory_ID,
            dropship=False,
            supplier_sku=self.product.supplier_SKU,
            price=self.product.purchase_price,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=models.Supplier.PRODUCT_OPTION_ID,
            option_value_id=self.new_supplier.product_option_value_ID,
        )
        self.assertEqual(5, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetSupplier(ProductUpdaterTest, TestSetSupplier):
    pass


class TestPartialRangeUpdaterSetSupplier(PartialProductUpdaterTest, TestSetSupplier):
    pass


class TestNoUpdateRangeUpdaterSetSupplier(NoChangeProductUpdaterTest, TestSetSupplier):
    pass


class TestSetSupplierSKU(BaseUpdaterMethodTest):
    def setup_test(self):
        self.product_option_value_ID = "6546156"
        self.option_ID = self.updater.SUPPLIER_SKU_PRODUCT_OPTION_ID
        self.mock_CCAPI.get_option_value_id.return_value = self.product_option_value_ID
        self.original_supplier_SKU = self.product.supplier_SKU
        self.new_supplier_SKU = "TY03923"
        self.updater.set_supplier_SKU(self.new_supplier_SKU)

    def update_DB_test(self):
        self.assertEqual(self.new_supplier_SKU, self.product.supplier_SKU)

    def no_DB_update_test(self):
        self.assertEqual(self.original_supplier_SKU, self.product.supplier_SKU)

    def update_CC_test(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=self.new_supplier_SKU, create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.product_option_value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetSupplierSKU(ProductUpdaterTest, TestSetSupplierSKU):
    pass


class TestPartialRangeUpdaterSetSupplierSKU(
    PartialProductUpdaterTest, TestSetSupplierSKU
):
    pass


class TestNoUpdateRangeUpdaterSetSupplierSKU(
    NoChangeProductUpdaterTest, TestSetSupplierSKU
):
    pass


class TestSetBarcode(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_barcode = self.product.barcode
        self.new_barcode = "46161654615"
        self.updater.set_barcode(self.new_barcode)

    def update_DB_test(self):
        self.assertEqual(self.new_barcode, self.product.barcode)

    def no_DB_update_test(self):
        self.assertEqual(self.original_barcode, self.product.barcode)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_barcode.assert_called_once_with(
            product_id=self.product.product_ID, barcode=self.new_barcode
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetBarcode(ProductUpdaterTest, TestSetBarcode):
    pass


class TestPartialRangeUpdaterSetBarcode(PartialProductUpdaterTest, TestSetBarcode):
    pass


class TestNoUpdateRangeUpdaterSetBarcode(NoChangeProductUpdaterTest, TestSetBarcode):
    pass


class TestSetPurchasePrice(BaseUpdaterMethodTest):
    def setup_test(self):
        self.option_ID = self.updater.PURCHASE_PRICE_PRODUCT_OPTION_ID
        self.value_ID = "2849829"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID
        self.original_purchase_price = self.product.purchase_price
        self.new_purchase_price = "11.99"
        self.updater.set_purchase_price(float(self.new_purchase_price))

    def update_DB_test(self):
        self.assertEqual(Decimal(self.new_purchase_price), self.product.purchase_price)

    def no_DB_update_test(self):
        self.assertEqual(self.original_purchase_price, self.product.purchase_price)

    def update_CC_test(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID,
            value="{:.2f}".format(float(self.new_purchase_price)),
            create=True,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetPurchasePrice(ProductUpdaterTest, TestSetPurchasePrice):
    pass


class TestPartialRangeUpdaterSetPurchasePrice(
    PartialProductUpdaterTest, TestSetPurchasePrice
):
    pass


class TestNoUpdateRangeUpdaterSetPurchasePrice(
    NoChangeProductUpdaterTest, TestSetPurchasePrice
):
    pass


class TestSetVATRate(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_VAT_rate = self.product.VAT_rate
        self.new_VAT_rate = models.VATRate.objects.create(
            VAT_rate_ID="28", name="Strange VAT", percentage=0.58
        )
        self.updater.set_VAT_rate(self.new_VAT_rate)

    def update_DB_test(self):
        self.assertEqual(self.new_VAT_rate, self.product.VAT_rate)

    def no_DB_update_test(self):
        self.assertEqual(self.original_VAT_rate, self.product.VAT_rate)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_vat_rate_by_id.assert_called_once_with(
            product_ids=[self.product.product_ID],
            vat_rate_id=self.new_VAT_rate.VAT_rate_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetVATRate(ProductUpdaterTest, TestSetVATRate):
    pass


class TestPartialRangeUpdaterVATRate(PartialProductUpdaterTest, TestSetVATRate):
    pass


class TestNoUpdateRangeUpdaterSetVATRate(NoChangeProductUpdaterTest, TestSetVATRate):
    pass


class TestSetPrice(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_price = self.product.price
        self.new_price = "58.70"
        self.updater.set_price(float(self.new_price))

    def update_DB_test(self):
        self.assertEqual(Decimal(self.new_price), self.product.price)

    def no_DB_update_test(self):
        self.assertEqual(self.original_price, self.product.price)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_base_price.assert_called_once_with(
            product_id=self.product.product_ID, price=float(self.new_price)
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetPrice(ProductUpdaterTest, TestSetPrice):
    pass


class TestPartialRangeUpdaterPrice(PartialProductUpdaterTest, TestSetPrice):
    pass


class TestNoUpdateRangeUpdaterSetPrice(NoChangeProductUpdaterTest, TestSetPrice):
    pass


class TestSetRetailPrice(BaseUpdaterMethodTest):
    def setup_test(self):
        self.option_ID = self.updater.RETAIL_PRICE_PRODUCT_OPTION_ID
        self.value_ID = "94651564"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID
        self.original_retail_price = self.product.retail_price
        self.new_retail_price = "12.50"
        self.updater.set_retail_price(float(self.new_retail_price))

    def update_DB_test(self):
        self.assertEqual(Decimal(self.new_retail_price), self.product.retail_price)

    def no_DB_update_test(self):
        self.assertEqual(self.original_retail_price, self.product.retail_price)

    def update_CC_test(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID,
            value="{:.2f}".format(float(self.new_retail_price)),
            create=True,
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetRetailPrice(ProductUpdaterTest, TestSetRetailPrice):
    pass


class TestPartialRangeUpdaterRetailPrice(PartialProductUpdaterTest, TestSetRetailPrice):
    pass


class TestNoUpdateRangeUpdaterSetRetailPrice(
    NoChangeProductUpdaterTest, TestSetRetailPrice
):
    pass


class TestSetRetailPriceNone(BaseUpdaterMethodTest):
    def setup_test(self):
        self.option_ID = self.updater.RETAIL_PRICE_PRODUCT_OPTION_ID
        self.original_retail_price = self.product.retail_price
        self.updater.set_retail_price(None)

    def update_DB_test(self):
        self.assertIsNone(self.product.retail_price)

    def no_DB_update_test(self):
        self.assertEqual(self.original_retail_price, self.product.retail_price)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.option_ID,
            option_value_id=0,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetRetailPriceNone(ProductUpdaterTest, TestSetRetailPriceNone):
    pass


class TestPartialRangeUpdaterSetRetailPriceNone(
    PartialProductUpdaterTest, TestSetRetailPriceNone
):
    pass


class TestNoUpdateRangeUpdaterSetRetailPriceNone(
    NoChangeProductUpdaterTest, TestSetRetailPriceNone
):
    pass


class TestSetBrand(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_brand = self.product.brand
        self.new_brand = models.Brand.objects.create(
            name="Things", product_option_value_ID="2849298"
        )
        self.updater.set_brand(self.new_brand)

    def update_DB_test(self):
        self.assertEqual(self.new_brand, self.product.brand)

    def no_DB_update_test(self):
        self.assertEqual(self.original_brand, self.product.brand)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.new_brand.PRODUCT_OPTION_ID,
            option_value_id=self.new_brand.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetBrand(ProductUpdaterTest, TestSetBrand):
    pass


class TestPartialRangeUpdaterSetBrand(PartialProductUpdaterTest, TestSetBrand):
    pass


class TestNoUpdateRangeUpdaterSetBrand(NoChangeProductUpdaterTest, TestSetBrand):
    pass


class TestSetManufacturer(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_manufacturer = self.product.manufacturer
        self.new_manufacturer = models.Manufacturer.objects.create(
            name="Things", product_option_value_ID="94111651"
        )
        self.updater.set_manufacturer(self.new_manufacturer)

    def update_DB_test(self):
        self.assertEqual(self.new_manufacturer, self.product.manufacturer)

    def no_DB_update_test(self):
        self.assertEqual(self.original_manufacturer, self.product.manufacturer)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.new_manufacturer.PRODUCT_OPTION_ID,
            option_value_id=self.new_manufacturer.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetManufacturer(ProductUpdaterTest, TestSetManufacturer):
    pass


class TestPartialRangeUpdaterSetManufacturer(
    PartialProductUpdaterTest, TestSetManufacturer
):
    pass


class TestNoUpdateRangeUpdaterSetManufacturer(
    NoChangeProductUpdaterTest, TestSetManufacturer
):
    pass


class TestSetPackageType(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_package_type = self.product.package_type
        self.new_package_type = models.PackageType.objects.create(
            name="Big Box",
            product_option_value_ID="7816165",
            large_letter_compatible=False,
        )
        self.updater.set_package_type(self.new_package_type)

    def update_DB_test(self):
        self.assertEqual(self.new_package_type, self.product.package_type)

    def no_DB_update_test(self):
        self.assertEqual(self.original_package_type, self.product.package_type)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.new_package_type.PRODUCT_OPTION_ID,
            option_value_id=self.new_package_type.product_option_value_ID,
        )
        self.mock_CCAPI.set_product_scope.assert_called_once_with(
            product_id=self.product.product_ID,
            weight=self.product.weight_grams,
            height=0,
            length=0,
            width=0,
            large_letter_compatible=self.new_package_type.large_letter_compatible,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetPackageType(ProductUpdaterTest, TestSetPackageType):
    pass


class TestPartialRangeUpdaterSetPackageType(
    PartialProductUpdaterTest, TestSetPackageType
):
    pass


class TestNoUpdateRangeUpdaterSetPackageType(
    NoChangeProductUpdaterTest, TestSetPackageType
):
    pass


class TestSetInternationalShipping(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_international_shipping = self.product.international_shipping
        self.new_international_shipping = models.InternationalShipping.objects.create(
            name="International Expedited", product_option_value_ID="41649886"
        )
        self.updater.set_international_shipping(self.new_international_shipping)

    def update_DB_test(self):
        self.assertEqual(
            self.new_international_shipping, self.product.international_shipping
        )

    def no_DB_update_test(self):
        self.assertEqual(
            self.original_international_shipping, self.product.international_shipping
        )

    def update_CC_test(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.new_international_shipping.PRODUCT_OPTION_ID,
            option_value_id=self.new_international_shipping.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetInternationalShipping(
    ProductUpdaterTest, TestSetInternationalShipping
):
    pass


class TestPartialRangeUpdaterSetInternationalShipping(
    PartialProductUpdaterTest, TestSetInternationalShipping
):
    pass


class TestNoUpdateRangeUpdaterSetInternationalShipping(
    NoChangeProductUpdaterTest, TestSetInternationalShipping
):
    pass


class TestSetBays(BaseUpdaterMethodTest):
    def setup_test(self):
        self.warehouse = models.Warehouse.objects.create(
            name="Warehouse", abriviation="WH", warehouse_ID="39347239"
        )
        self.bay_1 = models.Bay.objects.create(
            name="Bay 1", bay_ID="28493", warehouse=self.warehouse
        )
        self.bay_2 = models.Bay.objects.create(
            name="Bay 2", bay_ID="95641", warehouse=self.warehouse
        )
        self.bay_3 = models.Bay.objects.create(
            name="Bay 3", bay_ID="61354", warehouse=self.warehouse
        )
        self.bay_4 = models.Bay.objects.create(
            name="Bay 4", bay_ID="756131", warehouse=self.warehouse
        )
        self.bay_5 = models.Bay.objects.create(
            name="Bay 5", bay_ID="115648", warehouse=self.warehouse
        )
        self.original_bays = [self.bay_1, self.bay_2, self.bay_3]
        self.new_bays = [self.bay_3, self.bay_4, self.bay_5]
        self.product.bays.set(self.original_bays)
        mock_existing_bays = [Mock(id=bay.bay_ID) for bay in self.original_bays]
        self.mock_CCAPI.get_bays_for_product.return_value = mock_existing_bays
        self.updater.set_bays(self.new_bays)

    def update_DB_test(self):
        self.assertEqual(self.new_bays, list(self.product.bays.all()))

    def no_DB_update_test(self):
        self.assertEqual(self.original_bays, list(self.product.bays.all()))

    def update_CC_test(self):
        self.mock_CCAPI.get_bays_for_product.assert_called_once_with(
            self.product.product_ID
        )
        remove_bays_calls = [
            call(self.product.product_ID, bay.bay_ID)
            for bay in (self.bay_1, self.bay_2)
        ]
        self.mock_CCAPI.remove_warehouse_bay_from_product.assert_has_calls(
            remove_bays_calls
        )
        self.assertEqual(
            2, len(self.mock_CCAPI.remove_warehouse_bay_from_product.mock_calls)
        )
        add_bays_calls = [
            call(self.product.product_ID, bay.bay_ID)
            for bay in (self.bay_4, self.bay_5)
        ]
        self.mock_CCAPI.add_warehouse_bay_to_product.assert_has_calls(add_bays_calls)
        self.assertEqual(
            2, len(self.mock_CCAPI.add_warehouse_bay_to_product.mock_calls)
        )
        self.assertEqual(5, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetBays(ProductUpdaterTest, TestSetBays):
    pass


class TestPartialRangeUpdaterSetBays(PartialProductUpdaterTest, TestSetBays):
    pass


class TestNoUpdateRangeUpdaterSetBays(NoChangeProductUpdaterTest, TestSetBays):
    pass


class TestSetWeight(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_weight = self.product.weight_grams
        self.new_weight = 560
        self.updater.set_weight(self.new_weight)

    def update_DB_test(self):
        self.assertEqual(self.new_weight, self.product.weight_grams)

    def no_DB_update_test(self):
        self.assertEqual(self.original_weight, self.product.weight_grams)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_scope.assert_called_once_with(
            product_id=self.product.product_ID,
            weight=self.new_weight,
            height=0,
            length=0,
            width=0,
            large_letter_compatible=self.product.package_type.large_letter_compatible,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetWeight(ProductUpdaterTest, TestSetWeight):
    pass


class TestPartialRangeUpdaterSetWeight(PartialProductUpdaterTest, TestSetWeight):
    pass


class TestNoUpdateRangeUpdaterSetWeight(NoChangeProductUpdaterTest, TestSetWeight):
    pass


class TestSetLength(BaseUpdaterMethodTest):
    def setup_test(self):
        self.option_ID = self.updater.LENGTH_PRODUCT_OPTION_ID
        self.value_ID = "3840233"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID
        self.original_length = self.product.length_mm
        self.new_length = 568
        self.updater.set_length(self.new_length)

    def update_DB_test(self):
        self.assertEqual(self.new_length, self.product.length_mm)

    def no_DB_update_test(self):
        self.assertEqual(self.original_length, self.product.length_mm)

    def update_CC_test(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=str(self.new_length), create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetLength(ProductUpdaterTest, TestSetLength):
    pass


class TestPartialRangeUpdaterSetLength(PartialProductUpdaterTest, TestSetLength):
    pass


class TestNoUpdateRangeUpdaterSetLength(NoChangeProductUpdaterTest, TestSetLength):
    pass


class TestSetHeight(BaseUpdaterMethodTest):
    def setup_test(self):
        self.option_ID = self.updater.HEIGHT_PRODUCT_OPTION_ID
        self.value_ID = "9816156"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID
        self.original_height = self.product.height_mm
        self.new_height = 715
        self.updater.set_height(self.new_height)

    def update_DB_test(self):
        self.assertEqual(self.new_height, self.product.height_mm)

    def no_DB_update_test(self):
        self.assertEqual(self.original_height, self.product.height_mm)

    def update_CC_test(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=str(self.new_height), create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetHeight(ProductUpdaterTest, TestSetHeight):
    pass


class TestPartialRangeUpdaterSetHeight(PartialProductUpdaterTest, TestSetHeight):
    pass


class TestNoUpdateRangeUpdaterSetHeight(NoChangeProductUpdaterTest, TestSetHeight):
    pass


class TestSetWidth(BaseUpdaterMethodTest):
    def setup_test(self):
        self.option_ID = self.updater.WIDTH_PRODUCT_OPTION_ID
        self.value_ID = "1324864"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID
        self.original_width = self.product.width_mm
        self.new_width = 715
        self.updater.set_width(self.new_width)

    def update_DB_test(self):
        self.assertEqual(self.new_width, self.product.width_mm)

    def no_DB_update_test(self):
        self.assertEqual(self.original_width, self.product.width_mm)

    def update_CC_test(self):
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=str(self.new_width), create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetWidth(ProductUpdaterTest, TestSetWidth):
    pass


class TestPartialRangeUpdaterSetWidth(PartialProductUpdaterTest, TestSetWidth):
    pass


class TestNoUpdateRangeUpdaterSetWidth(NoChangeProductUpdaterTest, TestSetWidth):
    pass


class TestSetGender(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_gender = self.product.gender
        self.new_gender = models.Gender.objects.create(
            name="childrens",
            product_option_value_ID="89461456",
            readable_name="Childrens",
        )
        self.updater.set_gender(self.new_gender)

    def update_DB_test(self):
        self.assertEqual(self.new_gender, self.product.gender)

    def no_DB_update_test(self):
        self.assertEqual(self.original_gender, self.product.gender)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.new_gender.PRODUCT_OPTION_ID,
            option_value_id=self.new_gender.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetGender(ProductUpdaterTest, TestSetGender):
    pass


class TestPartialRangeUpdaterSetGender(PartialProductUpdaterTest, TestSetGender):
    pass


class TestNoUpdateRangeUpdaterSetGender(NoChangeProductUpdaterTest, TestSetGender):
    pass


class TestSetGenderNone(BaseUpdaterMethodTest):
    def setup_test(self):
        self.original_gender = self.product.gender
        self.updater.set_gender(None)

    def update_DB_test(self):
        self.assertIsNone(self.product.gender)

    def no_DB_update_test(self):
        self.assertEqual(self.original_gender, self.product.gender)

    def update_CC_test(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=models.Gender.PRODUCT_OPTION_ID,
            option_value_id=0,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetGenderNone(ProductUpdaterTest, TestSetGenderNone):
    pass


class TestPartialRangeUpdaterSetGenderNone(
    PartialProductUpdaterTest, TestSetGenderNone
):
    pass


class TestNoUpdateRangeUpdaterSetGenderNone(
    NoChangeProductUpdaterTest, TestSetGenderNone
):
    pass


class TestSetProductOptionLink(BaseUpdaterMethodTest):
    def setup_test(self):
        self.product_option = self.size_product_option
        self.original_value = self.updater.product_option_value_link_model.objects.get(
            product=self.product,
            product_option_value__product_option=self.product_option,
        ).product_option_value
        self.new_value = self.large_product_option_value
        self.updater.set_product_option_link(self.new_value)

    def update_DB_test(self):
        self.assertEqual(
            self.new_value,
            self.updater.product_option_value_link_model.objects.get(
                product=self.product,
                product_option_value__product_option=self.product_option,
            ).product_option_value,
        )

    def no_DB_update_test(self):
        self.assertEqual(
            self.original_value,
            self.updater.product_option_value_link_model.objects.get(
                product=self.product,
                product_option_value__product_option=self.product_option,
            ).product_option_value,
        )

    def update_CC_test(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.product_option.product_option_ID,
            option_value_id=self.new_value.product_option_value_ID,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetProductOptionLink(
    ProductUpdaterTest, TestSetProductOptionLink
):
    pass


class TestPartialRangeUpdaterSetProductOptionLink(
    PartialProductUpdaterTest, TestSetProductOptionLink
):
    pass


class TestNoUpdateRangeUpdaterSetProductOptionLink(
    NoChangeProductUpdaterTest, TestSetProductOptionLink
):
    pass


class TestRemoveProductOptionLink(BaseUpdaterMethodTest):
    def setup_test(self):
        self.product_option = self.size_product_option
        self.product_option_value = self.updater.product_option_value_link_model.objects.get(
            product=self.product,
            product_option_value__product_option=self.product_option,
        ).product_option_value
        self.updater.remove_product_option_link(self.product_option_value)

    def update_DB_test(self):
        self.assertFalse(
            self.updater.product_option_value_link_model.objects.filter(
                product=self.product,
                product_option_value__product_option=self.product_option,
            ).exists()
        )

    def no_DB_update_test(self):
        self.assertTrue(
            self.updater.product_option_value_link_model.objects.filter(
                product=self.product,
                product_option_value__product_option=self.product_option,
            ).exists()
        )

    def update_CC_test(self):
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.product_option.product_option_ID,
            option_value_id=0,
        )
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterRemoveProductOptionLink(
    ProductUpdaterTest, TestRemoveProductOptionLink
):
    pass


class TestPartialRangeUpdaterRemoveProductOptionLink(
    PartialProductUpdaterTest, TestRemoveProductOptionLink
):
    pass


class TestNoUpdateRangeUpdaterRemoveProductOptionLink(
    NoChangeProductUpdaterTest, TestRemoveProductOptionLink
):
    pass


class TestSetDateCreated(BaseUpdaterMethodTest):
    def setup_test(self):
        self.option_ID = self.updater.DATE_CREATED_PRODUCT_OPTION_ID
        self.value_ID = "38492"
        self.mock_CCAPI.get_option_value_id.return_value = self.value_ID
        self.original_date_created = self.product.date_created
        self.updater.set_date_created()
        self.assertEqual(self.original_date_created, self.product.date_created)

    def update_DB_test(self):
        self.assertEqual(self.original_date_created, self.product.date_created)

    def no_DB_update_test(self):
        self.assertEqual(self.original_date_created, self.product.date_created)

    def update_CC_test(self):
        date_string = self.original_date_created.strftime("%Y-%m-%d")
        self.mock_CCAPI.get_option_value_id.assert_called_once_with(
            option_id=self.option_ID, value=date_string, create=True
        )
        self.mock_CCAPI.set_product_option_value.assert_called_once_with(
            product_ids=[self.product.product_ID],
            option_id=self.option_ID,
            option_value_id=self.value_ID,
        )
        self.assertEqual(2, len(self.mock_CCAPI.mock_calls))


class TestRangeUpdaterSetDateCreated(ProductUpdaterTest, TestSetDateCreated):
    pass


class TestPartialRangeUpdaterSetDateCreated(
    PartialProductUpdaterTest, TestSetDateCreated
):
    pass


class TestNoUpdateRangeUpdaterSetDateCreated(
    NoChangeProductUpdaterTest, TestSetDateCreated
):
    pass
