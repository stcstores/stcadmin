"""Models managing Linnworks stock levels."""

import linnapi
from django.db import models, transaction

from inventory.models import BaseProduct, StockLevelHistory

from .linnworks_export_files import StockLevelExport


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


class StockLevelExportManager(models.Manager):
    """Model manager for the StockLevelUpdate model."""

    @transaction.atomic()
    def create_update(self, export=None):
        """Update stock level records from most recent Linnworks export."""
        export = export or StockLevelExport()
        if self.filter(export_time__date=export.export_date.date()).exists():
            return None
        update = self.model(export_time=export.export_date)
        update.save()
        for row in export.rows:
            if (
                row[export.IS_COMPOSITE_PARENT] == export.TRUE
                or int(row[export.QUANTITY]) < 1
            ):
                continue
            try:
                product = BaseProduct.objects.get(sku=row[export.SKU])
            except BaseProduct.DoesNotExist:
                raise ValueError(f"Could not find product {row[export.SKU]}.")
            record = StockLevelExportRecord(
                stock_level_update=update,
                product=product,
                in_order_book=int(row[export.IN_ORDER_BOOK]),
                stock_level=int(row[export.QUANTITY]),
                purchase_price=product.purchase_price,
            )
            record.save()
        return update


class StockLevelExportUpdate(models.Model):
    """Model for recording stock level updates from exports."""

    export_time = models.DateTimeField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = StockLevelExportManager()

    class Meta:
        """Meta class for StockLevelExportUpdate."""

        verbose_name = "Stock Level Export Update"
        verbose_name_plural = "Stock Level Export Updates"
        ordering = ["-export_time"]
        get_latest_by = "export_time"

    def __str__(self):
        date = self.export_time.strftime("%c")
        return f"Stock Level Update {date}"

    def stock_count(self):
        """Return the total number of items in stock."""
        return self.stock_level_records.aggregate(models.Sum("stock_level"))[
            "stock_level__sum"
        ]

    def stock_value(self):
        """Return the total number of items in stock."""
        return self.stock_level_records.aggregate(models.Sum("stock_value"))[
            "stock_value__sum"
        ]


class StockLevelExportRecord(models.Model):
    """Model for storing stock levels from Linnworks exports."""

    stock_level_update = models.ForeignKey(
        StockLevelExportUpdate,
        related_name="stock_level_records",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        BaseProduct, related_name="stock_level_records", on_delete=models.CASCADE
    )
    in_order_book = models.PositiveIntegerField()
    stock_level = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=7, decimal_places=2)
    stock_value = models.DecimalField(max_digits=7, decimal_places=2)

    def save(self, *args, **kwargs):
        """Set the stock value attribute."""
        self.stock_value = self.purchase_price * self.stock_level
        super().save(*args, **kwargs)

    class Meta:
        """Meta class for DailyStockLevel."""

        verbose_name = "Stock Level Export Record"
        verbose_name_plural = "Stock Levels Export Records"

        unique_together = ("stock_level_update", "product")

        order_with_respect_to = "stock_level_update"
