"""ProductCreator class."""

import datetime
import logging
import sys
import threading

import cc_products

from inventory import models

from .productbase import ProductEditorBase

logger = logging.getLogger('product_creation')


class ProductCreator(ProductEditorBase):
    """Create new Cloud Commerce Product from data in session."""

    def __new__(self, product_data):
        """Create new product and return it's range ID."""
        self.product_data = product_data
        title = self.product_data[self.BASIC][self.TITLE]
        self.product_range = cc_products.create_range(title)
        self.product_range.options[self.INCOMPLETE].selected = True
        t = threading.Thread(target=self.create_product, args=[self])
        t.setDaemon(True)
        t.start()
        return self.product_range.id

    def create_product(self):
        """Create new Cloud Commerce Product from data in session."""
        try:
            if self.product_data[self.TYPE] == self.SINGLE:
                self.create_single_product(self)
            elif self.product_data[self.TYPE] == self.VARIATION:
                self.create_variation_product(self)
            self.product_range.options[self.INCOMPLETE].selected = False
        except Exception as e:
            logger.error(
                'Product Creation Error: %s', ' '.join(sys.argv),
                exc_info=sys.exc_info())
            self.product_range.delete()
            raise e

    def create_single_product(self):
        """Create a single (non variation) product."""
        data = DataSanitizer(
            self.product_data[self.BASIC],
            self.product_data[self.PRODUCT_INFO])
        option_data = self.product_data[self.LISTING_OPTIONS]
        data[self.OPTIONS] = {k: v for k, v in option_data.items() if v}
        self.add_variation(self, **data)

    def sanitize_data(self, universal_data, basic_data):
        """Clean data from basic_info or variation_info page."""
        basic_fields = (
            self.BARCODE, self.PURCHASE_PRICE, self.RETAIL_PRICE,
            self.STOCK_LEVEL, self.SUPPLIER, self.SUPPLIER_SKU, self.WEIGHT,
            self.PACKAGE_TYPE, self.BRAND, self.MANUFACTURER, self.GENDER)
        universal_fields = (
            self.DESCRIPTION, self.AMAZON_BULLET_POINTS,
            self.AMAZON_SEARCH_TERMS)
        data = {field: universal_data[field] for field in universal_fields}
        data.update({field: basic_data[field] for field in basic_fields})
        data[self.VAT_RATE] = basic_data[self.PRICE][self.VAT_RATE]
        data[self.PRICE] = basic_data[self.PRICE][self.EX_VAT]
        for key in (self.LENGTH, self.WIDTH, self.HEIGHT):
            data[key] = basic_data[self.DIMENSIONS][key]
        department_id = self.product_data[self.PRODUCT_INFO][
            self.DEPARTMENT][self.DEPARTMENT]
        data[self.DEPARTMENT] = models.Warehouse.objects.get(
            warehouse_id=department_id).name
        if self.LOCATION in basic_data:
            data[self.BAYS] = basic_data[self.LOCATION]
        else:
            data[self.BAYS] = basic_data[self.DEPARTMENT][self.BAYS]
        if not data[self.BARCODE]:
            data[self.BARCODE] = models.get_barcode()
        for field in (self.AMAZON_SEARCH_TERMS, self.AMAZON_BULLET_POINTS):
            if not data[field][0]:
                data[field] = None
        return data

    def create_variation_product(self):
        """Create a variation product."""
        variations = [
            {k: v for k, v in d.items() if k != 'used'}
            for d in self.product_data[self.UNUSED_VARIATIONS] if d['used']]
        if not all([var.keys() == variations[0].keys() for var in variations]):
            raise Exception('Non matching variation keys.')
        for variation in variations:
            data = self.get_variation_data(self, variation)
            option_data = self.get_variation_option_data(self, variation)
            data[self.OPTIONS] = {k: v for k, v in variation.items()}
            data[self.OPTIONS].update(
                {k: v for k, v in option_data.items() if v})
            self.add_variation(self, **data)
        for key in variations[0]:
            self.product_range.options[key].variable = True

    def get_variation_data(self, variation):
        """Return sanitized data for variation."""
        variation_infos = self.product_data[self.VARIATION_INFO]
        for variation_info in variation_infos:
            if all([key in variation_info for key in variation]):
                if all([variation_info[k] == v for k, v in variation.items()]):
                    break
        else:
            raise Exception('Variation not found.')
        data = DataSanitizer(
            self.product_data[self.BASIC],
            self.product_data[self.PRODUCT_INFO],
            variation_info=variation_info)
        return data

    def get_variation_option_data(self, variation):
        """Return correct data for given variation."""
        all_option_data = self.product_data[self.VARIATION_LISTING_OPTIONS]
        for data in all_option_data:
            if all([key in data for key in variation]):
                if all([data[k] == v for k, v in variation.items()]):
                    return data

    def add_variation(self, **kwargs):
        """Add single variation to Range."""
        product = self.product_range.add_product(
            kwargs[self.BARCODE], kwargs[self.DESCRIPTION],
            kwargs[self.VAT_RATE])
        product.handling_time = 1
        product.department = kwargs[self.DEPARTMENT]
        product.bays = kwargs[self.BAYS]
        product.price = kwargs[self.PRICE]
        product.purchase_price = kwargs[self.PURCHASE_PRICE]
        product.retail_price = kwargs[self.RETAIL_PRICE]
        product.stock_level = kwargs[self.STOCK_LEVEL]
        product.supplier = kwargs[self.SUPPLIER]
        product.weight = kwargs[self.WEIGHT]
        product.height = kwargs[self.HEIGHT]
        product.height = kwargs[self.HEIGHT]
        product.width = kwargs[self.WIDTH]
        product.length = kwargs[self.LENGTH]
        product.package_type = kwargs[self.PACKAGE_TYPE]
        product.brand = kwargs[self.BRAND]
        product.manufacturer = kwargs[self.MANUFACTURER]
        product.date_created = datetime.datetime.now()
        if kwargs[self.SUPPLIER_SKU]:
            product.supplier_sku = kwargs[self.SUPPLIER_SKU]
        if kwargs[self.GENDER]:
            product.gender = kwargs[self.GENDER]
        if kwargs[self.AMAZON_BULLET_POINTS]:
            product.amazon_bullets = kwargs[self.AMAZON_BULLET_POINTS]
        if kwargs[self.AMAZON_SEARCH_TERMS]:
            product.amazon_search_terms = kwargs[self.AMAZON_SEARCH_TERMS]
        if kwargs[self.PACKAGE_TYPE] in (self.HEAVY_AND_LARGE, self.COURIER):
            product.international_shipping = self.EXPRESS
        else:
            product.international_shipping = self.STANDARD
        for option_name, option_value in kwargs[self.OPTIONS].items():
            product.options[option_name] = option_value


class DataSanitizer(ProductEditorBase):
    """Return dict of kwargs for product creation from form data."""

    SIMPLE_FIELDS = (
        ProductEditorBase.PURCHASE_PRICE, ProductEditorBase.RETAIL_PRICE,
        ProductEditorBase.STOCK_LEVEL, ProductEditorBase.SUPPLIER,
        ProductEditorBase.SUPPLIER_SKU, ProductEditorBase.WEIGHT,
        ProductEditorBase.PACKAGE_TYPE, ProductEditorBase.BRAND,
        ProductEditorBase.MANUFACTURER, ProductEditorBase.GENDER,
        ProductEditorBase.DESCRIPTION, ProductEditorBase.AMAZON_BULLET_POINTS,
        ProductEditorBase.AMAZON_SEARCH_TERMS)
    LIST_FIELDS = (
        ProductEditorBase.AMAZON_SEARCH_TERMS,
        ProductEditorBase.AMAZON_BULLET_POINTS)
    DIMENSION_FIELDS = (
        ProductEditorBase.LENGTH, ProductEditorBase.WIDTH,
        ProductEditorBase.HEIGHT)

    def __new__(self, basic_info, product_info, variation_info=None):
        """Clean data from basic_info or variation_info page."""
        product_data = {}
        product_data.update(basic_info)
        product_data.update(product_info)
        if variation_info is not None:
            product_data.update(variation_info)
        from pprint import pprint
        pprint(product_data)
        kwargs = self.sanitize_product_data(self, product_data)
        print()
        pprint(kwargs)
        return kwargs

    def sanitize_product_data(self, product_data):
        """Convert product data from form to arg dict."""
        data = self.get_simple_fields(self, product_data)
        self.set_location_data(self, product_data, data)
        self.set_list_fields(self, product_data, data)
        self.set_list_fields(self, product_data, data)
        self.set_barcode(self, product_data, data)
        self.set_dimension_fields(self, product_data, data)
        self.set_vat_price(self, product_data, data)
        return data

    def get_simple_fields(self, product_data):
        """Create data dict with fields that do not require processing set."""
        return {field: product_data[field] for field in self.SIMPLE_FIELDS}

    def set_location_data(self, product_data, data):
        """Set location and department data."""
        department_id = product_data[self.DEPARTMENT][self.DEPARTMENT]
        data[self.DEPARTMENT] = models.Warehouse.objects.get(
            warehouse_id=department_id).name
        if self.LOCATION in product_data:
            data[self.BAYS] = product_data[self.LOCATION]
        else:
            data[self.BAYS] = product_data[self.DEPARTMENT][self.BAYS]

    def set_dimension_fields(self, product_data, data):
        """Set dimension data."""
        for key in self.DIMENSION_FIELDS:
            data[key] = product_data[self.DIMENSIONS][key]

    def set_list_fields(self, product_data, data):
        """Set data from list fields."""
        for field in self.LIST_FIELDS:
            if not data[field][0]:
                data[field] = None

    def set_barcode(self, product_data, data):
        """Set barcode from database if not provided."""
        if not product_data[self.BARCODE]:
            data[self.BARCODE] = models.get_barcode()
        else:
            data[self.BARCODE] = product_data[self.BARCODE]

    def set_vat_price(self, product_data, data):
        """Set price and VAT rate data."""
        data[self.VAT_RATE] = product_data[self.PRICE][self.VAT_RATE]
        data[self.PRICE] = product_data[self.PRICE][self.EX_VAT]
