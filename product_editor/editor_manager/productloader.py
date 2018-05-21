"""The ProductLoader class."""

from pprint import pprint

import cc_products

from inventory import models

from .productbase import ProductEditorBase


class ProductLoader(ProductEditorBase):
    """Load Cloud Commerce Product data for product editor."""

    def __new__(self, range_id):
        """Load product data."""
        self.range_id = range_id
        self.product_range = cc_products.get_range(self.range_id)
        self.data = {self.RANGE_ID: self.range_id}
        self.data[self.TYPE] = self.get_product_type(self, self.product_range)
        self.data[self.BASIC] = self.get_basic(self, self.product_range)
        self.data[self.PRODUCT_INFO] = self.get_product_data(
            self, self.product_range.products[0])
        self.data[self.LISTING_OPTIONS] = self.get_listing_options(
            self, self.product_range.products[0])
        pprint(self.data)
        return self.data

    def get_warehouse_id(self, warehouse_name):
        """Return the ID of a warehouse by name."""
        return models.Warehouse.objects.get(name=warehouse_name).warehouse_id

    def get_dimension_data(self, product):
        """Return form data for the dimensions field."""
        return {
            self.HEIGHT: product.height, self.LENGTH: product.length,
            self.WIDTH: product.width}

    def get_location_data(self, product):
        """Return form data for the location field."""
        bay_ids = product.bays
        bays = models.Bay.objects.filter(bay_id__in=bay_ids)
        warehouse_id = bays[0].warehouse.warehouse_id
        return {self.WAREHOUSE: warehouse_id, self.BAYS: bay_ids}

    def get_product_type(self, product_range):
        """Return product type form data."""
        return self.SINGLE  # TEMP
        if len(product_range.products) > 1:
            return self.VARIATION
        else:
            return self.SINGLE

    def get_basic(self, product_range):
        """Return data for the Basic Info page."""
        data = {
            self.TITLE: product_range.name,
            self.DESCRIPTION: product_range.description,
            self.DEPARTMENT: self.get_warehouse_id(
                self, product_range.department),
            self.AMAZON_BULLET_POINTS: product_range.products[
                0].amazon_bullets,
            self.AMAZON_SEARCH_TERMS: product_range.products[
                0].amazon_search_terms,
        }
        return data

    def get_product_data(self, product):
        """Return data for the Product Info or Variation Info page."""
        data = {
            self.BARCODE: product.barcode,
            self.PURCHASE_PRICE: product.purchase_price,
            self.PRICE: {
                self.VAT_RATE: product.vat_rate, self.EX_VAT: product.price},
            self.RETAIL_PRICE: product.retail_price,
            self.STOCK_LEVEL: product.stock_level,
            self.LOCATION: self.get_location_data(self, product),
            self.SUPPLIER: product.supplier.factory_name,
            self.SUPPLIER_SKU: product.supplier_sku,
            self.WEIGHT: product.weight,
            self.DIMENSIONS: self.get_dimension_data(self, product),
            self.PACKAGE_TYPE: product.package_type,
            self.BRAND: product.brand,
            self.MANUFACTURER: product.manufacturer,
            self.GENDER: product.gender,
        }
        return data

    def get_listing_options(self, product):
        """Return data for the Listing Options page."""
        return dict(product.options)
