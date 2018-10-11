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

    def __repr__(self):
        return (
            f"Stock for {self.product_sku} changed by {self.user} at "
            f"{self.timestamp.strftime('%H:%M %d-%m-%Y')}"
        )

    def __str__(self):
        return self.__repr__()

    def get_user_name(self):
        """Return the name of the user who made the stock change."""
        return self.user.get_full_name()
