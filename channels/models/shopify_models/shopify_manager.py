"""Models for managing the Shopify channel."""

import time

import shopify_api_py
from shopify_api_py.exceptions import ProductNotFoundError


class ShopifyManager:
    """Methods for updating Shopify inventory information."""

    REQUEST_PAUSE = 0.51

    ACTIVE = "active"
    DRAFT = "draft"

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
    @shopify_api_py.shopify_api_session
    def get_collections(cls):
        """Return a list of all Shopify custom collections."""
        return shopify_api_py.products.get_all_custom_collections()

    @classmethod
    @shopify_api_py.shopify_api_session
    def add_product_to_collection(cls, product_id, collection_id):
        """Add a Shopify product to a collection.

        Args:
            product_id (int): The ID of the product.
            collection_id (int): The ID of the collection.
        """
        shopify_api_py.products.add_product_to_collection(
            product_id=product_id, collection_id=collection_id
        )

    @classmethod
    @shopify_api_py.shopify_api_session
    def remove_product_from_collection(cls, product_id, collection_id):
        """Remove a Shopify product from a collection.

        Args:
            product_id (int): The ID of the product.
            collection_id (int): The ID of the collection.
        """
        shopify_api_py.products.remove_product_from_collection(
            product_id=product_id, collection_id=collection_id
        )

    @classmethod
    @shopify_api_py.shopify_api_session
    def remove_product_from_all_collections(cls, product_id):
        """Remove a Shopify product from all collections.

        Args:
            product_id (int): The ID of the product.
            collection_id (int): The ID of the collection.
        """
        collects = shopify_api_py.products.shopify.Collect.find(product_id=product_id)
        for collect in collects:
            collect.destroy()

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
        if total_stock == 0 and product.status == cls.ACTIVE:
            cls._set_product_status(product, cls.DRAFT)
        elif total_stock > 0 and product.status == cls.DRAFT:
            cls._set_product_status(product, cls.ACTIVE)

    @classmethod
    def _set_product_status(cls, product, status):
        product.status = status
        product.save()
        time.sleep(cls.REQUEST_PAUSE)

    @classmethod
    @shopify_api_py.shopify_api_session
    def _hide_product(cls, product):
        product.status = cls.DRAFT
        product.save()

    @classmethod
    @shopify_api_py.shopify_api_session
    def _unhide_product(cls, product):
        product.status = cls.ACTIVE
        product.published_at = product.updated_at
        product.save()


class ShopifyStockManager:
    """Provides methods for managing Shopify stock."""

    @classmethod
    def update_out_of_stock(cls):
        """Hide out of stock items and unhide in stock items."""
        for product in cls._get_products():
            cls._update_product_status(product)

    @classmethod
    def _update_product_status(cls, product):
        stock_level = cls._get_stock_level(product)
        hidden = cls._product_is_hidden(product)
        if stock_level == 0 and hidden is False:
            ShopifyManager._hide_product(product)
        elif stock_level != 0 and hidden is True:
            ShopifyManager._unhide_product(product)

    @staticmethod
    def _get_products():
        return ShopifyManager._get_products()

    @staticmethod
    def _get_stock_level(product):
        return sum((variant.inventory_quantity for variant in product.variants))

    @staticmethod
    def _product_is_hidden(product):
        return product.status == ShopifyManager.DRAFT
