"""Models for the order app."""

from django.db import models

from inventory.models import Supplier


class ProductSale(models.Model):
    """Model for product sales."""

    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    sku = models.CharField(max_length=25, blank=True, null=True)
    channel_sku = models.CharField(max_length=25, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    weight = models.PositiveIntegerField(blank=True, null=True)
    quantity = models.PositiveIntegerField()
    supplier = models.ForeignKey(
        Supplier, blank=True, null=True, on_delete=models.PROTECT
    )

    purchase_price = models.PositiveIntegerField(blank=True, null=True)
    tax = models.PositiveIntegerField(blank=True, null=True)
    unit_price = models.PositiveIntegerField(blank=True, null=True)
    item_price = models.PositiveIntegerField(blank=True, null=True)
    item_total_before_tax = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        """Meta class for the ProductSale model."""

        verbose_name = "Product Sale"
        verbose_name_plural = "Product Sales"
        unique_together = ("order", "sku")

    def total_weight(self):
        """Return the combined weight of this item."""
        return self.weight * self.quantity

    def _channel_fee_paid(self):
        if self.order.channel is None:
            return 0
        channel_fee = self.order.channel.channel_fee
        return int(float(self.item_price / 100) * channel_fee)

    def _purchase_price_total(self):
        return self.purchase_price * self.quantity
