"""The stock change model."""

from django.contrib.auth import get_user_model
from django.db import models, transaction

from .product import BaseProduct


class StockLevelHistoryManager(models.Manager):
    """Model manager for the StockLevelHistory model."""

    def new_user_stock_level_update(self, product, user, stock_level):
        """Create a stock level change by a user."""
        return self._update_stock_level(
            product=product, source=self.model.USER, user=user, stock_level=stock_level
        )

    def new_import_stock_level_update(self, product, stock_level):
        """Create a stock level change from a Linnworks import."""
        return self._update_stock_level(
            product=product,
            source=self.model.IMPORT,
            user=None,
            stock_level=stock_level,
        )

    def new_api_stock_level_update(self, product, stock_level):
        """Create a stock level change from a Linnworks import."""
        return self._update_stock_level(
            product=product, source=self.model.API, user=None, stock_level=stock_level
        )

    @transaction.atomic
    def _update_stock_level(self, product, stock_level, source, user):
        previous_change = self.filter(product=product).last()
        if previous_change is not None and stock_level == previous_change.stock_level:
            return None
        new_update = self.model(
            source=source,
            user=user,
            product=product,
            stock_level=stock_level,
            previous_change=previous_change,
        )
        new_update.save()
        return new_update


class StockLevelHistory(models.Model):
    """Log stock level changes."""

    USER = "U"
    IMPORT = "I"
    API = "A"

    source = models.CharField(
        choices=((USER, "User"), (IMPORT, "Import"), (API, "API")), max_length=1
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
