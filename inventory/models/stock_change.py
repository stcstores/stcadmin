"""The stock change model."""

from django.contrib.auth import get_user_model
from django.db import models, transaction

from .product import BaseProduct


class StockLevelHistoryManager(models.Manager):
    """Model manager for the StockLevelHistory model."""

    @transaction.atomic
    def new_user_stock_level_update(self, product, user, stock_level):
        """Create a stock level change by a user."""
        previous_change = self.latest_update(product)
        if previous_change is not None and stock_level == previous_change.stock_level:
            return None
        new_update = self.model(
            source=self.model.USER,
            user=user,
            product=product,
            stock_level=stock_level,
            previous_change=previous_change,
        )
        new_update.save()
        product.latest_stock_change = new_update
        product.save()
        return new_update

    @transaction.atomic
    def new_import_stock_level_update(self, product, stock_level):
        """Create a stock level change from a Linnworks import."""
        previous_change = self.latest_update(product)
        if previous_change is not None and stock_level == previous_change.stock_level:
            return None
        new_update = self.model(
            source=self.model.IMPORT,
            product=product,
            stock_level=stock_level,
            previous_change=previous_change,
        )
        new_update.save()
        product.latest_stock_change = new_update
        product.save()
        return new_update

    def latest_update(self, product):
        """Return the most recent stock level change for a product or None if none exist."""
        try:
            return self.filter(product=product).last()
        except self.model.DoesNotExist:
            return None


class StockLevelHistory(models.Model):
    """Log stock level changes."""

    USER = "U"
    IMPORT = "I"

    source = models.CharField(
        choices=((USER, "User"), (IMPORT, "Import")), max_length=1
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="stock_change_history",
    )
    product = models.ForeignKey(
        BaseProduct, on_delete=models.CASCADE, related_name="stock_level_history"
    )
    stock_level = models.PositiveIntegerField()
    previous_change = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )
    timestamp = models.DateTimeField(auto_now=True)

    objects = StockLevelHistoryManager()

    class Meta:
        """Meta class for StockLevelHistory."""

        verbose_name = "Stock Level History"
        verbose_name_plural = "Stock Level History"
        ordering = ("timestamp",)
