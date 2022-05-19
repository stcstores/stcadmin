"""Models for the order app."""

from django.db import models

from inventory.models import Supplier


class ProductSale(models.Model):
    """Model for product sales."""

    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    sku = models.CharField(max_length=25, null=True)
    channel_sku = models.CharField(max_length=25, null=True)
    name = models.TextField(null=True)
    weight = models.PositiveIntegerField(null=True)
    quantity = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()
    supplier = models.ForeignKey(
        Supplier, blank=True, null=True, on_delete=models.PROTECT
    )
    purchase_price = models.PositiveIntegerField(blank=True, null=True)
    vat = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        """Meta class for the ProductSale model."""

        verbose_name = "Product Sale"
        verbose_name_plural = "Product Sales"
        unique_together = ("order", "sku")

    def total_weight(self):
        """Return the combined weight of this item."""
        return self.weight * self.quantity

    def _price_paid(self):
        return self.price * self.quantity

    def _vat_paid(self):
        return self.vat

    def _channel_fee_paid(self):
        channel_fee = self.order.channel.channel_fee
        return int(float(self._price_paid() / 100) * channel_fee)

    def _purchase_price_total(self):
        return self.purchase_price * self.quantity
