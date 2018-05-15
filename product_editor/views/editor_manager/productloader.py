from pprint import pprint

import cc_products

from .productbase import ProductEditorBase


class ProductLoader(ProductEditorBase):
    """Load Cloud Commerce Product data for product editor."""

    def __new__(self, range_id):
        self.range_id = range_id
        self.product_range = cc_products.get_range(self.range_id)
        self.data = {self.RANGE_ID: self.range_id}
        self.data[self.TYPE] = self.get_product_type(self, self.product_range)
        self.data[self.BASIC] = self.get_basic(self, self.product_range)
        self.data[self.LISTING_OPTIONS] = self.get_listing_options(
            self, self.product_range.products[0])
        pprint(self.data)
        return self.data

    def get_product_type(self, product_range):
        return self.SINGLE  # TEMP
        if len(product_range.products) > 1:
            return self.VARIATION
        else:
            return self.SINGLE

    def get_basic(self, product_range):
        data = {
            self.TITLE: product_range.name,
            self.DESCRIPTION: product_range.description,
            self.AMAZON_BULLET_POINTS: product_range.products[
                0].amazon_bullets,
            self.AMAZON_SEARCH_TERMS: product_range.products[
                0].amazon_search_terms,
        }
        return data

    def get_listing_options(self, product):
        return dict(product.options)
