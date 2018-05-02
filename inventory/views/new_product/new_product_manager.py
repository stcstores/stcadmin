"""Classes for manageing product data stored in the session."""

import datetime
import json
import threading

import cc_products

from inventory import models


class NewProductBase:
    """Base class for new product classes."""

    VARIATION = 'variation'
    SINGLE = 'single'
    NEW_PRODUCT = 'new_product_data'
    BASIC = 'basic_info'
    TYPE = 'type'
    VARIATION_OPTIONS = 'variation_options'
    UNUSED_VARIATIONS = 'unused_variations'
    LISTING_OPTIONS = 'listing_options'
    VARIATION_INFO = 'variation_info'
    VARIATION_LISTING_OPTIONS = 'variation_listing_options'
    FINISH = 'finish'


class Page:
    """Container for new product form pages."""

    def __init__(self, name, identifier, manager, url=None):
        """Set page properties."""
        self.name = name
        self.identifier = identifier
        if url is None:
            self.url = 'inventory:new_product_{}'.format(self.identifier)
        else:
            self.url = 'inventory:{}'.format(url)
        self.manager = manager

    @property
    def data(self):
        """Return data stored in the session for this page."""
        data = self.manager.session[self.manager.NEW_PRODUCT].get(
            self.identifier, None)
        return data

    @data.setter
    def data(self, data):
        """Store data in the session for this page."""
        self.manager.session[self.manager.NEW_PRODUCT][self.identifier] = data
        self.manager.session.modified = True


class NewProductManager(NewProductBase):
    """Access new product data stored in session."""

    def __init__(self, request):
        """Set object properties."""
        self.request = request
        self.session = request.session
        if self.NEW_PRODUCT not in self.session:
            self.session[self.NEW_PRODUCT] = {}
        self.session.modified = True
        self.basic_info = Page('Basic Info', self.BASIC, self)
        self.listing_options = Page(
            'Listing Options', self.LISTING_OPTIONS, self)
        self.variation_options = Page(
            'Variation Options', self.VARIATION_OPTIONS, self)
        self.unused_variations = Page(
            'Unused Variations', self.UNUSED_VARIATIONS, self)
        self.variation_info = Page('Variation Info', self.VARIATION_INFO, self)
        self.variation_listing_options = Page(
            'Variation Listing Options', self.VARIATION_LISTING_OPTIONS, self)
        self.finish = Page('Finish', self.FINISH, self)
        self.data = self.session.get(self.NEW_PRODUCT, None)
        self.pages = (
            self.basic_info, self.listing_options, self.variation_options,
            self.variation_info, self.variation_listing_options, self.finish)
        self.single_product_pages = (
            self.basic_info, self.listing_options, self.finish)
        self.variation_product_pages = (
            self.basic_info, self.variation_options, self.unused_variations,
            self.variation_info, self.variation_listing_options, self.finish)
        if self.product_type == self.VARIATION:
            self.current_pages = self.variation_product_pages
        elif self.product_type == self.SINGLE:
            self.current_pages = self.single_product_pages
        else:
            self.current_pages = (self.basic_info, )

    @property
    def product_type(self):
        """Type of product, Single or Variation."""
        product_data = self.session.get(self.NEW_PRODUCT, None)
        if product_data is not None:
            return product_data.get(self.TYPE, None)
        else:
            return None

    @product_type.setter
    def product_type(self, product_type):
        product_data = self.session.get(self.NEW_PRODUCT, None)
        product_data[self.TYPE] = product_type
        self.session.modified = True

    @property
    def variations(self):
        """Return variation combinations for product."""
        combinations = [
            {k: v for k, v in d.items() if k != 'used'}
            for d in self.unused_variations.data if d['used']]
        return combinations

    def delete_product(self):
        """Clear all new product data from session."""
        self.session[self.NEW_PRODUCT] = {}

    def save_json(self, outfile):
        """Output new product data as JSON to outfile."""
        data = self.product_data
        return json.dump(data, outfile, indent=4, sort_keys=True)

    @property
    def product_data(self):
        """Return all new product data."""
        return self.session[self.NEW_PRODUCT]

    def create_product(self):
        """Create new Cloud Commerce Product from data in session."""
        return NewProduct(self.product_data)


class NewProduct(NewProductBase):
    """Create new Cloud Commerce Product from data in session."""

    BARCODE = 'barcode'
    DESCRIPTION = 'description'
    PRICE = 'price'
    VAT_RATE = 'vat_rate'
    EX_VAT = 'ex_vat'
    DEPARTMENT = 'department'
    BAYS = 'bays'
    PURCHASE_PRICE = 'purchase_price'
    STOCK_LEVEL = 'stock_level'
    SUPPLIER = 'supplier'
    SUPPLIER_SKU = 'supplier_sku'
    WEIGHT = 'weight'
    HEIGHT = 'height'
    WIDTH = 'width'
    LENGTH = 'length'
    PACKAGE_TYPE = 'package_type'
    BRAND = 'brand'
    MANUFACTURER = 'manufacturer'
    GENDER = 'gender'
    AMAZON_BULLET_POINTS = 'amazon_bullet_points'
    AMAZON_SEARCH_TERMS = 'amazon_search_terms'
    OPTIONS = 'options'
    LOCATION = 'location'
    DIMENSIONS = 'dimensions'
    HEAVY_AND_LARGE = 'Heavy and Large'
    COURIER = 'Courier'
    STANDARD = 'Standard'
    EXPRESS = 'Express'

    def __new__(self, product_data):
        """Create new product and return it's range ID."""
        self.product_data = product_data
        title = self.product_data[self.BASIC]['title']
        self.product_range = cc_products.create_range(title)
        self.product_range.options['Incomplete'].selected = True
        t = threading.Thread(target=self.create_product, args=[self])
        t.setDaemon(True)
        t.start()
        return self.product_range.id

    def create_product(self):
        """Create new Cloud Commerce Product from data in session."""
        if self.product_data[self.TYPE] == self.SINGLE:
            self.create_single_product(self)
        elif self.product_data[self.TYPE] == self.VARIATION:
            self.create_variation_product(self)
        self.product_range.options['Incomplete'].selected = False

    def create_single_product(self):
        """Create a single (non variation) product."""
        data = self.sanitize_basic_data(self, self.product_data[self.BASIC])
        option_data = self.product_data[self.LISTING_OPTIONS]
        data[self.OPTIONS] = {k: v for k, v in option_data.items() if v}
        self.add_variation(self, **data)

    def sanitize_basic_data(self, basic_data):
        """Clean data from basic_info or variation_info page."""
        basic_fields = (
            self.BARCODE, self.PURCHASE_PRICE, self.STOCK_LEVEL,
            self.SUPPLIER, self.SUPPLIER_SKU, self.WEIGHT, self.PACKAGE_TYPE,
            self.BRAND, self.MANUFACTURER, self.GENDER)
        universal_fields = (
            self.DESCRIPTION, self.AMAZON_BULLET_POINTS,
            self.AMAZON_SEARCH_TERMS)
        data = {
            field: basic_data[field] for field in basic_fields}
        for key in universal_fields:
            data[key] = self.product_data[self.BASIC][key]
        data[self.VAT_RATE] = basic_data[self.PRICE][self.VAT_RATE]
        data[self.PRICE] = basic_data[self.PRICE][self.EX_VAT]
        for key in (self.LENGTH, self.WIDTH, self.HEIGHT):
            data[key] = basic_data[self.DIMENSIONS][key]
        department_id = self.product_data[self.BASIC][
            self.DEPARTMENT][self.DEPARTMENT]
        data[self.DEPARTMENT] = models.Warehouse.objects.get(
            warehouse_id=department_id).name
        if self.LOCATION in basic_data:
            data[self.BAYS] = basic_data[self.LOCATION]
        else:
            data[self.BAYS] = basic_data[self.DEPARTMENT][self.BAYS]
        if not data[self.BARCODE]:
            data[self.BARCODE] = models.get_barcode()
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
        for info in variation_infos:
            if all([key in info for key in variation]):
                if all([info[k] == v for k, v in variation.items()]):
                    break
        else:
            raise Exception('Variation not found.')
        data = self.sanitize_basic_data(self, info)
        return data

    def get_variation_option_data(self, variation):
        """Return correct data for given variation."""
        all_option_data = self.product_data[self.VARIATION_LISTING_OPTIONS]
        for data in all_option_data:
            if all([key in data for key in variation]):
                if all([data[k] == v for k, v in variation.items()]):
                    return data
        raise Exception('Option data not found.')

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
