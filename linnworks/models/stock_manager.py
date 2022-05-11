"""Models managing Linnworks stock levels."""

import linnapi
from django.db import models

from inventory.models import StockLevelHistory


class InitialStockLevel(models.Model):
    """Model for storing new product stock levels to be added to Linnworks."""

    sku = models.CharField(max_length=255, db_index=True, unique=True)
    stock_level = models.PositiveIntegerField()

    class Meta:
        """Meta class for the InitialStockLevel model."""

        verbose_name = "Initial Stock Level"
        verbose_name_plural = "Initial Stock Levels"


class StockManager:
    """Methods for managing Linnworks stock levels."""

    LOCATION_ID = "00000000-0000-0000-0000-000000000000"

    @classmethod
    def get_stock_level(cls, product):
        """
        Get the current stock level for a product.

        Args:
            product (inventory.models.BaseProduct): The product to retrieve the stock
                level for.

        """
        current_stock_level = cls.current_stock_level(product.sku)
        StockLevelHistory.objects.new_import_stock_level_update(
            product=product, stock_level=current_stock_level
        )
        return current_stock_level

    @classmethod
    def get_initial_stock_level(cls, product):
        """
        Get the temporary intial stock level for a new product.

        Args:
            product (inventory.models.BaseProduct): The product to retrieve the stock
                level for.

        """
        try:
            instance = InitialStockLevel.objects.get(sku=product.sku)
        except InitialStockLevel.DoesNotExist:
            return None
        else:
            return instance.stock_level

    @classmethod
    def set_stock_level(cls, product, user, new_stock_level, change_source=""):
        """
        Update the stock level for a product.

        Kwargs:
            product (inventory.models.BaseProduct): The product to update the stock
                level of.
            user (django.contrib.auth.User): The user performing the update.
            new_stock_level (int): The new stock level of the product.
        """
        current_stock_level = cls.current_stock_level(sku=product.sku)
        relative_stock_level_change = new_stock_level - current_stock_level
        change_source = change_source or f"Updated through STCAdmin by {user}"
        updated_stock_level_info = cls._set_stock_level_in_linnworks(
            sku=product.sku,
            relative_stock_level_change=relative_stock_level_change,
            change_source=change_source,
        )
        StockLevelHistory.objects.new_user_stock_level_update(
            product=product, user=user, stock_level=updated_stock_level_info.stock_level
        )
        return updated_stock_level_info.stock_level

    @classmethod
    def set_initial_stock_level(cls, product, user, new_stock_level, change_source=""):
        """
        Update the stock level for a product.

        Kwargs:
            product (inventory.models.BaseProduct): The product to update the stock
                level of.
            user (django.contrib.auth.User): The user performing the update.
            new_stock_level (int): The new stock level of the product.
        """
        instance = InitialStockLevel(sku=product.sku, stock_level=new_stock_level)
        instance.save()
        return instance.stock_level

    @classmethod
    @linnapi.linnworks_api_session
    def _get_stock_level__info_from_linnworks(cls, sku):
        """Return stock level information for a product SKU."""
        return linnapi.inventory.get_stock_level_by_sku(sku=sku)

    @classmethod
    @linnapi.linnworks_api_session
    def _set_stock_level_in_linnworks(
        cls, sku, relative_stock_level_change, change_source=""
    ):
        return linnapi.inventory.set_stock_level(
            changes=((sku, relative_stock_level_change),),
            location_id=cls.LOCATION_ID,
            change_source=change_source,
        )[0]

    @classmethod
    def stock_level_info(cls, sku):
        """Return stock level information for a product SKU."""
        return cls._get_stock_level__info_from_linnworks(sku)

    @classmethod
    def current_stock_level(cls, sku):
        """Return the current stock level for a product SKU."""
        stock_level_info = cls.stock_level_info(sku)
        return stock_level_info.stock_level
