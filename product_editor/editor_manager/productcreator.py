"""ProductCreator class."""

import datetime
import logging
import threading

import cc_products
from inventory import models
from product_editor import exceptions

from .productbase import ProductEditorBase

logger = logging.getLogger("product_creation")


class ProductSaver(ProductEditorBase):
    """Create new Cloud Commerce Product from data in session."""

    def __new__(self, product_data, user):
        """Create new product and return it's range ID."""
        self.product_data = product_data
        self.user = user
        self.product_range = self.get_product_range(self)
        self.product_range.options[self.INCOMPLETE].selected = True
        t = threading.Thread(target=self.create_product, args=[self])
        t.setDaemon(True)
        t.start()
        return self.product_range.id

    def get_product_range(self):
        """Return Product Range to be saved."""
        raise NotImplementedError()

    def create_product(self):
        """Create new Cloud Commerce Product from data in session."""
        try:
            if self.product_data[self.TYPE] == self.SINGLE:
                self.create_single_product(self)
            elif self.product_data[self.TYPE] == self.VARIATION:
                self.create_variation_product(self)
            self.product_range.options[self.INCOMPLETE].selected = False
        except Exception as e:
            logger.exception(f"Error creating product.", extra={"user": self.user})
            self.handle_error(self)
            raise e

    def create_single_product(self):
        """Create a single (non variation) product."""
        data = DataSanitizer(
            self.product_data[self.BASIC], self.product_data[self.PRODUCT_INFO]
        )
        option_data = self.product_data[self.LISTING_OPTIONS]
        data[self.OPTIONS] = {k: v for k, v in option_data.items() if v}
        self.add_variation(self, **data)

    def create_variation_product(self):
        """Create a variation product."""
        variations = self.get_variations(self)
        for variation in variations:
            data = self.get_variation_data(self, variation)
            option_data = self.get_variation_option_data(self, variation)
            data[self.OPTIONS] = {k: v for k, v in variation.items()}
            data[self.OPTIONS].update({k: v for k, v in option_data.items() if v})
            self.add_variation(self, **data)
        for key in variations[0]:
            self.product_range.options[key].variable = True
        if len(self.product_range.products) > 0:  # Range already contains products
            self.product_range.name = data[self.TITLE]
            self.product_range.description = data[self.DESCRIPTION]

    def get_variations(self):
        """Return list of variation option dicts."""
        form_data = self.product_data[self.UNUSED_VARIATIONS]
        variations = []
        for variation in [d for d in form_data if d[self.USED]]:
            variations.append(
                {
                    k: v
                    for k, v in variation.items()
                    if k not in (self.PRODUCT_ID, self.USED)
                }
            )
        if not all([var.keys() == variations[0].keys() for var in variations]):
            raise exceptions.VariationKeyMissmatch(variations)
        return variations

    def get_variation_data(self, variation):
        """Return sanitized data for variation."""
        variation_infos = self.product_data[self.VARIATION_INFO]
        for variation_info in variation_infos:
            if all([key in variation_info for key in variation]):
                if all([variation_info[k] == v for k, v in variation.items()]):
                    break
        else:
            raise exceptions.VariationNotFoundError(variation_info)
        data = DataSanitizer(
            self.product_data[self.BASIC],
            self.product_data[self.PRODUCT_INFO],
            variation_info=variation_info,
        )
        return data

    def get_variation_option_data(self, variation):
        """Return correct data for given variation."""
        all_option_data = self.product_data[self.VARIATION_LISTING_OPTIONS]
        for data in all_option_data:
            if all([key in data for key in variation]):
                if all([data[k] == v for k, v in variation.items()]):
                    return data
        raise exceptions.VariationNotFoundError(variation)

    def get_variation(self, **kwargs):
        """Return variation to be saved."""
        raise NotImplementedError()

    def add_variation(self, **kwargs):
        """Add single variation to Range."""
        product = self.get_variation(**kwargs)
        self.update_product(product, **kwargs)

    def get_new_product(self, **kwargs):
        """Add new Product to Range and return."""
        return self.product_range.add_product(
            kwargs[self.BARCODE], kwargs[self.DESCRIPTION], kwargs[self.VAT_RATE]
        )

    def handle_error(self):
        """Is called after an error saving the product."""
        pass

    def update_product(self, product, **kwargs):
        """Update product details from form data."""
        product.handling_time = 1
        product.department = kwargs[self.DEPARTMENT]
        product.bays = kwargs[self.BAYS]
        product.price = kwargs[self.PRICE]
        product.purchase_price = kwargs[self.PURCHASE_PRICE]
        product.supplier = kwargs[self.SUPPLIER]
        product.weight = kwargs[self.WEIGHT]
        product.height = kwargs[self.HEIGHT]
        product.height = kwargs[self.HEIGHT]
        product.width = kwargs[self.WIDTH]
        product.length = kwargs[self.LENGTH]
        product.package_type = kwargs[self.PACKAGE_TYPE]
        product.brand = kwargs[self.BRAND]
        product.manufacturer = kwargs[self.MANUFACTURER]
        if product.barcode != kwargs[self.BARCODE]:
            product.barcode = kwargs[self.BARCODE]
        if kwargs[self.RETAIL_PRICE]:
            product.retail_price = kwargs[self.RETAIL_PRICE]
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
            if option_name not in (self.PRODUCT_ID, self.RANGE_ID):
                product.options[option_name] = option_value
        if self.PRODUCT_ID not in kwargs or not kwargs[self.PRODUCT_ID]:
            product.date_created = datetime.datetime.now()


class ProductCreator(ProductSaver):
    """Create product in Cloud Commerce."""

    def get_product_range(self):
        """Return new product range."""
        title = self.product_data[self.BASIC][self.TITLE]
        return cc_products.create_range(title)

    def add_variation(self, **kwargs):
        """Add single variation to Range."""
        product = self.product_range.add_product(
            kwargs[self.BARCODE], kwargs[self.DESCRIPTION], kwargs[self.VAT_RATE]
        )
        self.update_product(self, product, **kwargs)

    def get_variation(self, **kwargs):
        """Return variation to be saved."""
        return self.get_new_product(**kwargs)

    def handle_error(self):
        """Delete the product if creation fails."""
        self.product_range.delete()

    def update_product(self, product, **kwargs):
        """Set initial stock level."""
        super().update_product(self, product, **kwargs)
        product.stock_level = kwargs[self.STOCK_LEVEL]


class ProductEditor(ProductSaver):
    """Update product in Cloud Commerce."""

    def get_product_range(self):
        """Return Product Range to be updated."""
        return cc_products.get_range(self.product_data[self.RANGE_ID])

    def add_variation(self, **kwargs):
        """Add single variation to Range."""
        product = self.get_variation(self, **kwargs)
        self.update_product(self, product, **kwargs)

    def get_variation(self, **kwargs):
        """Return variation to be saved."""
        if kwargs[self.PRODUCT_ID]:
            return cc_products.get_product(kwargs[self.PRODUCT_ID])
        else:
            return self.get_new_product(self, **kwargs)


class DataSanitizer(ProductEditorBase):
    """Return dict of kwargs for product creation from form data."""

    SIMPLE_FIELDS = (
        ProductEditorBase.BRAND,
        ProductEditorBase.DESCRIPTION,
        ProductEditorBase.GENDER,
        ProductEditorBase.MANUFACTURER,
        ProductEditorBase.PACKAGE_TYPE,
        ProductEditorBase.PRODUCT_ID,
        ProductEditorBase.PURCHASE_PRICE,
        ProductEditorBase.RETAIL_PRICE,
        ProductEditorBase.STOCK_LEVEL,
        ProductEditorBase.SUPPLIER,
        ProductEditorBase.SUPPLIER_SKU,
        ProductEditorBase.TITLE,
        ProductEditorBase.WEIGHT,
    )

    LIST_FIELDS = (
        ProductEditorBase.AMAZON_BULLET_POINTS,
        ProductEditorBase.AMAZON_SEARCH_TERMS,
    )
    DIMENSION_FIELDS = (
        ProductEditorBase.HEIGHT,
        ProductEditorBase.LENGTH,
        ProductEditorBase.WIDTH,
    )

    def __new__(self, basic_info, product_info, variation_info=None):
        """Clean data from basic_info or variation_info page."""
        product_data = {}
        product_data.update(basic_info)
        product_data.update(product_info)
        if variation_info is not None:
            product_data.update(variation_info)
        kwargs = self.sanitize_product_data(self, product_data)
        return kwargs

    def sanitize_product_data(self, product_data):
        """Convert product data from form to arg dict."""
        data = {}
        self.set_simple_fields(self, product_data, data)
        self.set_location_data(self, product_data, data)
        self.set_list_fields(self, product_data, data)
        self.set_barcode(self, product_data, data)
        self.set_dimension_fields(self, product_data, data)
        self.set_vat_price(self, product_data, data)
        return data

    def set_simple_fields(self, product_data, data):
        """Create data dict with fields that do not require processing set."""
        for key in self.SIMPLE_FIELDS:
            data[key] = product_data[key]

    def set_location_data(self, product_data, data):
        """Set location and department data."""
        data[self.DEPARTMENT] = models.Warehouse.objects.get(
            warehouse_id=product_data[self.DEPARTMENT]
        ).name
        data[self.BAYS] = product_data[self.LOCATION][self.BAYS]

    def set_dimension_fields(self, product_data, data):
        """Set dimension data."""
        for key in self.DIMENSION_FIELDS:
            data[key] = product_data[self.DIMENSIONS][key]

    def set_list_fields(self, product_data, data):
        """Set data from list fields."""
        for field in self.LIST_FIELDS:
            if product_data[field][0]:
                data[field] = product_data[field]
            else:
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
