"""The ProductLoader class."""

from pprint import pprint

import cc_products

from inventory import models
from product_editor import exceptions

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
        if self.data[self.TYPE] == self.SINGLE:
            self.data[self.LISTING_OPTIONS] = self.get_listing_options(
                self, self.product_range.products[0])
        elif self.data[self.TYPE] == self.VARIATION:
            self.data[self.VARIATION_OPTIONS], self.data[
                self.UNUSED_VARIATIONS] = self.get_variation_options(
                    self, self.product_range)
            self.data[self.EXISTING_VARIATIONS] = self.data[
                self.VARIATION_OPTIONS]
            self.data[self.VARIATION_INFO] = self.get_variation_info(
                self, self.product_range)
            self.data[
                self.VARIATION_LISTING_OPTIONS
            ] = self.get_variation_listing_options(
                self, self.product_range)
        pprint(self.data)
        return self.data

    def variations_combinations(self):
        """Return variation combinations for product."""
        combinations = [
            {k: v for k, v in d.items() if k not in
                (self.USED, self.PRODUCT_ID)}
            for d in self.data[self.UNUSED_VARIATIONS] if d[self.USED]]
        return combinations

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
        if len(bays) > 0:
            warehouse_id = bays[0].warehouse.warehouse_id
            return {self.WAREHOUSE: warehouse_id, self.BAYS: bay_ids}
        return {self.WAREHOUSE: '', self.BAYS: []}

    def get_product_type(self, product_range):
        """Return product type form data."""
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
            self.PRODUCT_ID: product.id}
        return data

    def get_listing_options(self, product):
        """Return data for the Listing Options page."""
        return dict(product.options)

    def get_variation_options(self, product_range):
        """Return data for the Variation Options page."""
        variable_options = product_range.variable_options
        variation_options = {o.name: [] for o in variable_options}
        unused_variation_data = []
        for product in product_range.products:
            variation = {self.USED: True, self.PRODUCT_ID: product.id}
            for option in variation_options:
                value = product.options[option]
                variation_options[option].append(value)
                variation[option] = value
            unused_variation_data.append(variation)
        return variation_options, unused_variation_data

    def product_matches_variation(product, variation):
        """Return True if variation matches the options of product."""
        return all([product.options[k] == v for k, v in variation.items()])

    def get_product_variations(self, product_range):
        """Return list of tuples containing a variation dict and product."""
        variations = self.variations_combinations(self)
        products = []
        for product in product_range.products:
            for variation in variations:
                if self.product_matches_variation(product, variation):
                    products.append((variation, product))
                    break
            else:
                raise exceptions.VariationNotFoundError(variation)
        return products

    def get_variation_info(self, product_range):
        """Return data for the Variation Info page."""
        variation_products = self.get_product_variations(self, product_range)
        variation_info_data = []
        for variation, product in variation_products:
            product_data = self.get_product_data(self, product)
            for key, value in variation.items():
                product_data[key] = value
            variation_info_data.append(product_data)
        return variation_info_data

    def get_variation_listing_options(self, product_range):
        """Return data for the Variation Listing Options page."""
        variation_products = self.get_product_variations(self, product_range)
        option_info_data = []
        for variation, product in variation_products:
            product_data = self.get_listing_options(self, product)
            for key, value in variation.items():
                product_data[key] = value
            product_data[self.PRODUCT_ID] = product.id
            option_info_data.append(product_data)
        return option_info_data
