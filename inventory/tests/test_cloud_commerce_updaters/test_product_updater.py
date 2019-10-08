from unittest.mock import Mock, call, patch

from home.tests.test_views.view_test import ViewTest
from inventory import models
from inventory.cloud_commerce_updater import PartialProductUpdater, ProductUpdater
from inventory.tests.test_models.test_products import SetupVariationProductRange


class ProductUpdaterTests:
    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_supplier(self, mock_CCAPI):
        mock_links = [Mock(link_id="829304"), Mock(link_id="384932")]
        mock_CCAPI.get_product_factory_links.return_value = mock_links
        original_supplier = self.product.supplier
        new_supplier = models.Supplier.objects.create(
            name="New Supplier",
            product_option_value_ID="23840938",
            factory_ID="34854392",
        )
        self.updater.set_supplier(new_supplier)
        if self.update_DB:
            self.assertEqual(new_supplier, self.product.supplier)
        else:
            self.assertEqual(original_supplier, self.product.supplier)
        if self.update_CC:
            mock_CCAPI.get_product_factory_links.assert_called_once_with(
                self.product.product_ID
            )
            for link in mock_links:
                mock_CCAPI.delete_product_factory_link.assert_any_call(link.link_id)
            self.assertEqual(2, len(mock_CCAPI.delete_product_factory_link.mock_calls))
            mock_CCAPI.update_product_factory_link.assert_called_once_with(
                product_id=self.product.product_ID,
                factory_id=new_supplier.factory_ID,
                dropship=False,
                supplier_sku=self.product.supplier_SKU,
                price=self.product.purchase_price,
            )
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=models.Supplier.PRODUCT_OPTION_ID,
                option_value_id=new_supplier.product_option_value_ID,
            )
            self.assertEqual(5, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_supplier_SKU(self, mock_CCAPI):
        product_option_value_ID = "6546156"
        option_ID = self.updater.SUPPLIER_SKU_PRODUCT_OPTION_ID
        mock_CCAPI.get_option_value_id.return_value = product_option_value_ID
        original_supplier_SKU = self.product.supplier_SKU
        new_supplier_SKU = "TY03923"
        self.updater.set_supplier_SKU(new_supplier_SKU)
        if self.update_DB:
            self.assertEqual(new_supplier_SKU, self.product.supplier_SKU)
        else:
            self.assertEqual(original_supplier_SKU, self.product.supplier_SKU)
        if self.update_CC:
            mock_CCAPI.get_option_value_id.assert_called_once_with(
                option_id=option_ID, value=new_supplier_SKU, create=True
            )
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=option_ID,
                option_value_id=product_option_value_ID,
            )
            self.assertEqual(2, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_barcode(self, mock_CCAPI):
        original_barcode = self.product.barcode
        new_barcode = "46161654615"
        self.updater.set_barcode(new_barcode)
        if self.update_DB:
            self.assertEqual(new_barcode, self.product.barcode)
        else:
            self.assertEqual(original_barcode, self.product.barcode)
        if self.update_CC:
            mock_CCAPI.set_product_barcode.assert_called_once_with(
                product_id=self.product.product_ID, barcode=new_barcode
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_purchase_price(self, mock_CCAPI):
        option_ID = self.updater.PURCHASE_PRICE_PRODUCT_OPTION_ID
        value_ID = "2849829"
        mock_CCAPI.get_option_value_id.return_value = value_ID
        original_purchase_price = self.product.purchase_price
        new_purchase_price = 11.99
        self.updater.set_purchase_price(new_purchase_price)
        if self.update_DB:
            self.assertEqual(new_purchase_price, self.product.purchase_price)
        else:
            self.assertEqual(original_purchase_price, self.product.purchase_price)
        if self.update_CC:
            mock_CCAPI.get_option_value_id.assert_called_once_with(
                option_id=option_ID,
                value="{:.2f}".format(new_purchase_price),
                create=True,
            )
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=option_ID,
                option_value_id=value_ID,
            )
            self.assertEqual(2, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_VAT_rate(self, mock_CCAPI):
        original_VAT_rate = self.product.VAT_rate
        new_VAT_rate = models.VATRate.objects.create(
            VAT_rate_ID="28", name="Strange VAT", percentage=0.58
        )
        self.updater.set_VAT_rate(new_VAT_rate)
        if self.update_DB:
            self.assertEqual(new_VAT_rate, self.product.VAT_rate)
        else:
            self.assertEqual(original_VAT_rate, self.product.VAT_rate)
        if self.update_CC:
            mock_CCAPI.set_product_vat_rate_by_id.assert_called_once_with(
                product_ids=[self.product.product_ID],
                vat_rate_id=new_VAT_rate.VAT_rate_ID,
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_price(self, mock_CCAPI):
        original_price = self.product.price
        new_price = 58.70
        self.updater.set_price(new_price)
        if self.update_DB:
            self.assertEqual(new_price, self.product.price)
        else:
            self.assertEqual(original_price, self.product.price)
        if self.update_CC:
            mock_CCAPI.set_product_base_price.assert_called_once_with(
                product_id=self.product.product_ID, price=new_price
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_retail_price(self, mock_CCAPI):
        option_ID = self.updater.RETAIL_PRICE_PRODUCT_OPTION_ID
        value_ID = "94651564"
        mock_CCAPI.get_option_value_id.return_value = value_ID
        original_retail_price = self.product.retail_price
        new_retail_price = 12.50
        self.updater.set_retail_price(new_retail_price)
        if self.update_DB:
            self.assertEqual(new_retail_price, self.product.retail_price)
        else:
            self.assertEqual(original_retail_price, self.product.retail_price)
        if self.update_CC:
            mock_CCAPI.get_option_value_id.assert_called_once_with(
                option_id=option_ID,
                value="{:.2f}".format(new_retail_price),
                create=True,
            )
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=option_ID,
                option_value_id=value_ID,
            )
            self.assertEqual(2, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_retail_price_None(self, mock_CCAPI):
        option_ID = self.updater.RETAIL_PRICE_PRODUCT_OPTION_ID
        original_retail_price = self.product.retail_price
        new_retail_price = None
        self.updater.set_retail_price(new_retail_price)
        if self.update_DB:
            self.assertEqual(new_retail_price, self.product.retail_price)
        else:
            self.assertEqual(original_retail_price, self.product.retail_price)
        if self.update_CC:
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=option_ID,
                option_value_id=0,
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_brand(self, mock_CCAPI):
        original_brand = self.product.brand
        new_brand = models.Brand.objects.create(
            name="Things", product_option_value_ID="2849298"
        )
        self.updater.set_brand(new_brand)
        if self.update_DB:
            self.assertEqual(new_brand, self.product.brand)
        else:
            self.assertEqual(original_brand, self.product.brand)
        if self.update_CC:
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=new_brand.PRODUCT_OPTION_ID,
                option_value_id=new_brand.product_option_value_ID,
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_manufacturer(self, mock_CCAPI):
        original_manufacturer = self.product.manufacturer
        new_manufacturer = models.Manufacturer.objects.create(
            name="Things", product_option_value_ID="94111651"
        )
        self.updater.set_manufacturer(new_manufacturer)
        if self.update_DB:
            self.assertEqual(new_manufacturer, self.product.manufacturer)
        else:
            self.assertEqual(original_manufacturer, self.product.manufacturer)
        if self.update_CC:
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=new_manufacturer.PRODUCT_OPTION_ID,
                option_value_id=new_manufacturer.product_option_value_ID,
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_package_type(self, mock_CCAPI):
        original_package_type = self.product.package_type
        new_package_type = models.PackageType.objects.create(
            name="Big Box",
            product_option_value_ID="7816165",
            large_letter_compatible=False,
        )
        self.updater.set_package_type(new_package_type)
        if self.update_DB:
            self.assertEqual(new_package_type, self.product.package_type)
        else:
            self.assertEqual(original_package_type, self.product.package_type)
        if self.update_CC:
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=new_package_type.PRODUCT_OPTION_ID,
                option_value_id=new_package_type.product_option_value_ID,
            )
            mock_CCAPI.set_product_scope.assert_called_once_with(
                product_id=self.product.product_ID,
                weight=self.product.weight_grams,
                height=0,
                length=0,
                width=0,
                large_letter_compatible=new_package_type.large_letter_compatible,
            )
            self.assertEqual(2, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_international_shipping(self, mock_CCAPI):
        original_international_shipping = self.product.international_shipping
        new_international_shipping = models.InternationalShipping.objects.create(
            name="International Expedited", product_option_value_ID="41649886"
        )
        self.updater.set_international_shipping(new_international_shipping)
        if self.update_DB:
            self.assertEqual(
                new_international_shipping, self.product.international_shipping
            )
        else:
            self.assertEqual(
                original_international_shipping, self.product.international_shipping
            )
        if self.update_CC:
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=new_international_shipping.PRODUCT_OPTION_ID,
                option_value_id=new_international_shipping.product_option_value_ID,
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_bays(self, mock_CCAPI):
        warehouse = models.Warehouse.objects.create(
            name="Warehouse", abriviation="WH", warehouse_ID="39347239"
        )
        bay_1 = models.Bay.objects.create(
            name="Bay 1", bay_ID="28493", warehouse=warehouse
        )
        bay_2 = models.Bay.objects.create(
            name="Bay 2", bay_ID="95641", warehouse=warehouse
        )
        bay_3 = models.Bay.objects.create(
            name="Bay 3", bay_ID="61354", warehouse=warehouse
        )
        bay_4 = models.Bay.objects.create(
            name="Bay 4", bay_ID="756131", warehouse=warehouse
        )
        bay_5 = models.Bay.objects.create(
            name="Bay 5", bay_ID="115648", warehouse=warehouse
        )
        original_bays = [bay_1, bay_2, bay_3]
        new_bays = [bay_3, bay_4, bay_5]
        self.product.bays.set(original_bays)
        mock_existing_bays = [Mock(id=bay.bay_ID) for bay in original_bays]
        mock_CCAPI.get_bays_for_product.return_value = mock_existing_bays
        self.updater.set_bays(new_bays)
        if self.update_DB:
            self.assertEqual(new_bays, list(self.product.bays.all()))
        else:
            self.assertEqual(original_bays, list(self.product.bays.all()))
        if self.update_CC:
            mock_CCAPI.get_bays_for_product.assert_called_once_with(
                self.product.product_ID
            )
            mock_CCAPI.remove_warehouse_bay_from_product.assert_has_calls(
                [call(self.product.product_ID, bay.bay_ID) for bay in (bay_1, bay_2)]
            )
            self.assertEqual(
                2, len(mock_CCAPI.remove_warehouse_bay_from_product.mock_calls)
            )
            mock_CCAPI.add_warehouse_bay_to_product.assert_has_calls(
                [call(self.product.product_ID, bay.bay_ID) for bay in (bay_4, bay_5)]
            )
            self.assertEqual(2, len(mock_CCAPI.add_warehouse_bay_to_product.mock_calls))
            self.assertEqual(5, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_weight(self, mock_CCAPI):
        original_weight = self.product.weight_grams
        new_weight = 560
        self.updater.set_weight(new_weight)
        if self.update_DB:
            self.assertEqual(new_weight, self.product.weight_grams)
        else:
            self.assertEqual(original_weight, self.product.weight_grams)
        if self.update_CC:
            mock_CCAPI.set_product_scope.assert_called_once_with(
                product_id=self.product.product_ID,
                weight=new_weight,
                height=0,
                length=0,
                width=0,
                large_letter_compatible=self.product.package_type.large_letter_compatible,
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_length(self, mock_CCAPI):
        option_ID = self.updater.LENGTH_PRODUCT_OPTION_ID
        value_ID = "3840233"
        mock_CCAPI.get_option_value_id.return_value = value_ID
        original_length = self.product.length_mm
        new_length = 568
        self.updater.set_length(new_length)
        if self.update_DB:
            self.assertEqual(new_length, self.product.length_mm)
        else:
            self.assertEqual(original_length, self.product.length_mm)
        if self.update_CC:
            mock_CCAPI.get_option_value_id.assert_called_once_with(
                option_id=option_ID, value=str(new_length), create=True
            )
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=option_ID,
                option_value_id=value_ID,
            )
            self.assertEqual(2, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_height(self, mock_CCAPI):
        option_ID = self.updater.HEIGHT_PRODUCT_OPTION_ID
        value_ID = "9816156"
        mock_CCAPI.get_option_value_id.return_value = value_ID
        original_height = self.product.height_mm
        new_height = 715
        self.updater.set_height(new_height)
        if self.update_DB:
            self.assertEqual(new_height, self.product.height_mm)
        else:
            self.assertEqual(original_height, self.product.height_mm)
        if self.update_CC:
            mock_CCAPI.get_option_value_id.assert_called_once_with(
                option_id=option_ID, value=str(new_height), create=True
            )
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=option_ID,
                option_value_id=value_ID,
            )
            self.assertEqual(2, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_width(self, mock_CCAPI):
        option_ID = self.updater.WIDTH_PRODUCT_OPTION_ID
        value_ID = "1324864"
        mock_CCAPI.get_option_value_id.return_value = value_ID
        original_width = self.product.width_mm
        new_width = 715
        self.updater.set_width(new_width)
        if self.update_DB:
            self.assertEqual(new_width, self.product.width_mm)
        else:
            self.assertEqual(original_width, self.product.width_mm)
        if self.update_CC:
            mock_CCAPI.get_option_value_id.assert_called_once_with(
                option_id=option_ID, value=str(new_width), create=True
            )
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=option_ID,
                option_value_id=value_ID,
            )
            self.assertEqual(2, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_gender(self, mock_CCAPI):
        original_gender = self.product.gender
        new_gender = models.Gender.objects.create(
            name="childrens",
            product_option_value_ID="89461456",
            readable_name="Childrens",
        )
        self.updater.set_gender(new_gender)
        if self.update_DB:
            self.assertEqual(new_gender, self.product.gender)
        else:
            self.assertEqual(original_gender, self.product.gender)
        if self.update_CC:
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=new_gender.PRODUCT_OPTION_ID,
                option_value_id=new_gender.product_option_value_ID,
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_gender_None(self, mock_CCAPI):
        original_gender = self.product.gender
        new_gender = None
        self.updater.set_gender(new_gender)
        if self.update_DB:
            self.assertEqual(new_gender, self.product.gender)
        else:
            self.assertEqual(original_gender, self.product.gender)
        if self.update_CC:
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=models.Gender.PRODUCT_OPTION_ID,
                option_value_id=0,
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_product_option_link(self, mock_CCAPI):
        product_option = self.size_product_option
        original_value = self.updater.product_option_value_link_model.objects.get(
            product=self.product, product_option_value__product_option=product_option
        ).product_option_value
        new_value = self.large_product_option_value
        self.updater.set_product_option_link(new_value)
        if self.update_DB:
            self.assertEqual(
                new_value,
                self.updater.product_option_value_link_model.objects.get(
                    product=self.product,
                    product_option_value__product_option=product_option,
                ).product_option_value,
            )
        else:
            self.assertEqual(
                original_value,
                self.updater.product_option_value_link_model.objects.get(
                    product=self.product,
                    product_option_value__product_option=product_option,
                ).product_option_value,
            )
        if self.update_CC:
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=product_option.product_option_ID,
                option_value_id=new_value.product_option_value_ID,
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_remove_product_option_link(self, mock_CCAPI):
        product_option = self.size_product_option
        product_option_value = self.updater.product_option_value_link_model.objects.get(
            product=self.product, product_option_value__product_option=product_option
        ).product_option_value
        self.updater.remove_product_option_link(product_option_value)
        if self.update_DB:
            self.assertFalse(
                self.updater.product_option_value_link_model.objects.filter(
                    product=self.product,
                    product_option_value__product_option=product_option,
                ).exists()
            )
        else:
            self.assertTrue(
                self.updater.product_option_value_link_model.objects.filter(
                    product=self.product,
                    product_option_value__product_option=product_option,
                ).exists()
            )
        if self.update_CC:
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=product_option.product_option_ID,
                option_value_id=0,
            )
            self.assertEqual(1, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))

    @patch("inventory.cloud_commerce_updater.product_updater.CCAPI")
    def test_set_date_created(self, mock_CCAPI):
        option_ID = self.updater.DATE_CREATED_PRODUCT_OPTION_ID
        value_ID = "38492"
        mock_CCAPI.get_option_value_id.return_value = value_ID
        original_date_created = self.product.date_created
        self.updater.set_date_created()
        self.assertEqual(original_date_created, self.product.date_created)
        if self.update_CC:
            date_string = original_date_created.strftime("%Y-%m-%d")
            mock_CCAPI.get_option_value_id.assert_called_once_with(
                option_id=option_ID, value=date_string, create=True
            )
            mock_CCAPI.set_product_option_value.assert_called_once_with(
                product_ids=[self.product.product_ID],
                option_id=option_ID,
                option_value_id=value_ID,
            )
            self.assertEqual(2, len(mock_CCAPI.mock_calls))
        else:
            self.assertEqual(0, len(mock_CCAPI.mock_calls))


class TestProductUpdater(SetupVariationProductRange, ProductUpdaterTests, ViewTest):
    updater_class = ProductUpdater
    update_DB = True
    update_CC = True

    def setUp(self):
        super(SetupVariationProductRange, self).setUp()
        self.product_edit = models.ProductEdit.create_product_edit(
            self.user, self.product_range
        )
        self.updater = self.updater_class(self.product, self.user)
        self.product_IDs = [_.product_ID for _ in self.product_range.products()]


class TestPartialProductUpdater(
    SetupVariationProductRange, ProductUpdaterTests, ViewTest
):
    updater_class = PartialProductUpdater
    update_DB = True
    update_CC = False

    def setUp(self):
        super(SetupVariationProductRange, self).setUp()
        self.product_edit = models.ProductEdit.create_product_edit(
            self.user, self.product_range
        )
        self.original_range = self.product_edit.product_range
        self.product_range = self.product_edit.partial_product_range
        self.product = self.product_range.products()[0]
        self.updater = self.updater_class(self.product, self.user)
        self.product_IDs = [_.product_ID for _ in self.product_range.products()]


class TestProductUpdaterWithoutDB(
    SetupVariationProductRange, ProductUpdaterTests, ViewTest
):
    updater_class = ProductUpdater
    update_DB = False
    update_CC = False

    def setUp(self):
        super(SetupVariationProductRange, self).setUp()
        self.product_edit = models.ProductEdit.create_product_edit(
            self.user, self.product_range
        )
        self.updater = self.updater_class(self.product, self.user)
        self.updater.update_DB = False
        self.updater.update_CC = False
        self.product_IDs = [_.product_ID for _ in self.product_range.products()]
