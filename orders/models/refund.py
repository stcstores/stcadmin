"""Model for refund tracking."""
from django.db import models
from django.shortcuts import reverse

from .order import Order
from .product_sale import ProductSale


class RefundReason(models.Model):
    """Model for reasons for refund requests."""

    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    auto_close = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Refund(models.Model):
    """Model for refund requests."""

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(ProductSale, on_delete=models.PROTECT)
    number_applied_to = models.PositiveIntegerField()
    reason = models.ForeignKey(RefundReason, on_delete=models.PROTECT)
    contact_contacted = models.BooleanField(default=False)
    refund_accepted = models.BooleanField(blank=True, null=True)
    refund_amount = models.PositiveIntegerField(blank=True, null=True)
    closed = models.BooleanField(default=False)

    def get_absolute_url(self):
        """Return the URL for this refund."""
        return reverse("orders:refund", kwargs={"pk": self.pk})
