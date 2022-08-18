"""Models for managing the Shopify channel."""

import time

import shopify_api_py
from shopify_api_py.exceptions import ProductNotFoundError


class ShopifyManager:
    """Methods for updating Shopify inventory information."""

    REQUEST_PAUSE = 0.51

    @classmethod
    def product_exists(cls, product_id):
        """Return True if product_id is an existant product ID on Shopify, otherwise False.

        Args:
            product_id (int): The product ID to check.

        Returns:
            bool: True if the product ID is found, otherwise False.
        """
        try:
            cls._get_product(product_id)
        except ProductNotFoundError:
            return False
        else:
            return True

    @classmethod
    def update_stock(cls):
        """Update Shopify product stock level and status."""
        stock_levels = cls._get_stock_levels()
        location_id = cls._get_location_id()
        products = cls._get_products()
        cls._update_stock_levels(
            products=products, location_id=location_id, stock_levels=stock_levels
        )

    @classmethod
    @shopify_api_py.shopify_api_session
    def _get_product(cls, product_id):
        return shopify_api_py.products.get_product_by_id(product_id=product_id)

    @classmethod
    @shopify_api_py.shopify_api_session
    def _get_variant(cls, variant_id):
        return shopify_api_py.products.get_variant_by_id(variant_id=variant_id)

    @classmethod
    @shopify_api_py.shopify_api_session
    def _get_inventory_item(cls, inventory_item_id):
        return shopify_api_py.products.get_inventory_item_by_id(
            inventory_item_id=inventory_item_id
        )

    @classmethod
    @shopify_api_py.shopify_api_session
    def _get_products(cls):
        return shopify_api_py.products.get_all_products()

    @classmethod
    @shopify_api_py.shopify_api_session
    def _get_location_id(cls):
        locations = shopify_api_py.locations.get_inventory_locations()
        return locations[0].id

    @classmethod
    def _update_variant_stock(cls, variant, location_id, stock_levels):
        new_stock_level = stock_levels[variant.sku]
        current_stock_level = variant.inventory_quantity
        if current_stock_level != new_stock_level:
            shopify_api_py.products.update_variant_stock(
                variant=variant,
                new_stock_level=new_stock_level,
                location_id=location_id,
            )
            time.sleep(cls.REQUEST_PAUSE)

    @classmethod
    def _update_product_status(cls, product):
        total_stock = sum([variant.inventory_quantity for variant in product.variants])
        if total_stock == 0 and product.status == "active":
            cls._set_product_status(product, "draft")
        elif total_stock > 0 and product.status == "draft":
            cls._set_product_status(product, "active")

    @classmethod
    def _set_product_status(cls, product, status):
        product.status = status
        product.save()
        time.sleep(cls.REQUEST_PAUSE)
