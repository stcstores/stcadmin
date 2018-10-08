"""The stock change model."""

from django.contrib.auth.models import User
from django.db import models


class StockChange(models.Model):
    """Log changes to product stock levels."""

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now=True)
    product_sku = models.CharField(max_length=11)
    product_id = models.CharField(max_length=50)
    stock_before = models.PositiveIntegerField()
    stock_after = models.PositiveIntegerField()

    class Meta:
        """Meta class for StockChangeLog."""

        verbose_name = "Stock Change"
        verbose_name_plural = "Stock Changes"
