"""Models managing Linnworks stock levels."""

from collections import defaultdict

import linnapi
from django.db import models, transaction

from inventory.models import BaseProduct, StockLevelHistory

from .config import LinnworksChannel
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
        available_stock_level = cls.available_stock_level(product.sku)
        StockLevelHistory.objects.new_import_stock_level_update(
            product=product, stock_level=available_stock_level
        )
        return available_stock_level

    @classmethod
    def get_stock_levels(cls, products):
        """
        Get the current stock level for multiple products.

        Args:
            products (queryset): Queryset of inventory.models.BaseProduct.

        """
        skus = products.values_list("sku", flat=True)
        stock_level_records = cls._get_multiple_stock_level_info_from_linnworks(*skus)
        with transaction.atomic():
            for product in products:
                StockLevelHistory.objects.new_import_stock_level_update(
                    product=product,
                    stock_level=stock_level_records[product.sku].stock_level,
                )
        return stock_level_records

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
        available_stock_level = cls.available_stock_level(sku=product.sku)
        relative_stock_level_change = new_stock_level - available_stock_level
        change_source = change_source or f"Updated through STCAdmin by {user}"
        updated_stock_level_info = cls._set_stock_level_in_linnworks(
            sku=product.sku,
            relative_stock_level_change=relative_stock_level_change,
            change_source=change_source,
        )
        StockLevelHistory.objects.new_user_stock_level_update(
            product=product, user=user, stock_level=updated_stock_level_info.stock_level
        )
        return updated_stock_level_info.available

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
        instance, created = InitialStockLevel.objects.get_or_create(
            sku=product.sku, defaults={"stock_level": new_stock_level}
        )
        if not created:
            instance.stock_level = new_stock_level
            instance.save()
        return instance.stock_level

    @classmethod
    def get_stock_level_history(cls, sku):
        """Return a history of stock level changes for a SKU."""
        records = cls._get_stock_level_history(sku)
        return [
            {
                "timestamp": record.timestamp,
                "stock_level": record.stock_level,
                "text": record.text,
                "relative_change": record.relative_change,
            }
            for record in records
        ]

    @classmethod
    def stock_level_info(cls, sku):
        """Return stock level information for a product SKU."""
        return cls._get_stock_level__info_from_linnworks(sku)

    @classmethod
    def available_stock_level(cls, sku):
        """Return the current stock level for a product SKU."""
        stock_level_info = cls.stock_level_info(sku)
        return stock_level_info.available

    @classmethod
    def recorded_stock_level(cls, *skus):
        """Return the latest stock level from stock level records."""
        update = StockLevelExportUpdate.objects.latest()
        records = StockLevelExportRecord.objects.filter(
            product__sku__in=skus, stock_level_update=update
        )
        output = {
            record.product.sku: {
                "total_stock_level": record.stock_level,
                "available_stock_level": record.available,
                "timestamp": update.export_time,
            }
            for record in records
        }
        for sku in skus:
            if sku not in output:
                output[sku] = {
                    "total_stock_level": 0,
                    "available_stock_level": 0,
                    "timestamp": update.export_time,
                }
        return output

    @classmethod
    def products_exist(cls, *skus):
        """Return True if all SKUs exist in Linnworks, otherwise False."""
        try:
            stock_level_ids = cls._get_stock_item_ids(*skus)
        except linnapi.exceptions.InvalidResponseError:
            return False
        if not set(skus).issubset(set(stock_level_ids.keys())):
            return False
        return True

    @classmethod
    def channel_links(cls, *skus):
        """Return channel linked items for SKUs."""
        links = cls._get_channel_linked_items(*skus)
        output = defaultdict(lambda: defaultdict(list))
        for sku, sku_links in links.items():
            for channel in LinnworksChannel.objects.all():
                for link in sku_links:
                    if (
                        link.source == channel.source
                        and link.sub_source == channel.sub_source
                    ):
                        link.url = channel.item_link(link.channel_reference_id)
                        output[sku][channel].append(link)
        return {
            sku: {channel: links for channel, links in output[sku].items()}
            for sku in output
        }

    @classmethod
    @linnapi.linnworks_api_session
    def _get_stock_item_ids(cls, *skus):
        """Return stock item IDs for one or more SKUs."""
        return linnapi.inventory.get_stock_item_ids_by_sku(*skus)

    @classmethod
    @linnapi.linnworks_api_session
    def _get_stock_level__info_from_linnworks(cls, sku):
        """Return stock level information for a product SKU."""
        return linnapi.inventory.get_stock_level_by_sku(sku=sku)

    @classmethod
    @linnapi.linnworks_api_session
    def _get_multiple_stock_level_info_from_linnworks(cls, *skus):
        """Return stock level information for multiple product SKUs."""
        if not skus:
            return {}
        return linnapi.inventory.get_stock_levels_by_skus(*skus)

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
    @linnapi.linnworks_api_session
    def _get_stock_level_history(cls, sku):
        return linnapi.inventory.get_stock_level_history_by_sku(
            sku=sku, location_id=cls.LOCATION_ID
        )

    @classmethod
    @linnapi.linnworks_api_session
    def _get_channel_linked_items(cls, *skus):
        return linnapi.inventory.get_channel_skus_by_skus(*skus)


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

    @property
    def available(self):
        """Return the available stock level."""
        return self.stock_level - self.in_order_book

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
        get_latest_by = "stock_level_update__export_time"
