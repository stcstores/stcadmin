"""Models for managing the Shopify channel."""

import time

import shopify_api_py
from django.db import models

from inventory.models import ProductExport


class ShopifyImport(models.Model):
    """Model for Shopify order imports."""

    created_at = models.DateTimeField(auto_now_add=True)


class ShopifyInventoryUpdater:
    """Methods for updating Shopify inventory information."""

    REQUEST_PAUSE = 0.51

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
    def _get_products(cls):
        """Return all Shopify products."""
        return shopify_api_py.products.get_all_products()

    @classmethod
    @shopify_api_py.shopify_api_session
    def _get_location_id(cls):
        """Return all Shopify products."""
        locations = shopify_api_py.locations.get_inventory_locations()
        return locations[0].id

    @classmethod
    def _get_stock_levels(cls):
        inventory_information = ProductExport.objects.latest("timestamp").as_table()
        stock_levels = {
            row["VAR_SKU"]: int(row["VAR_Stock"]) for row in inventory_information
        }
        return stock_levels

    @classmethod
    @shopify_api_py.shopify_api_session
    def _update_stock_levels(cls, products, location_id, stock_levels):
        for product in products:
            for variant in product.variants:
                cls._update_variant_stock(
                    variant=variant, location_id=location_id, stock_levels=stock_levels
                )
            cls._update_product_status(product)

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
