"""Model for refund tracking."""

from django.db import models
from django.shortcuts import reverse
from polymorphic.models import PolymorphicModel

from .order import Order
from .product_sale import ProductSale


class Refund(PolymorphicModel):
    """Model for refund requests."""

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    contact_contacted = models.BooleanField(default=False)
    refund_accepted = models.BooleanField(blank=True, null=True)
    refund_amount = models.PositiveIntegerField(blank=True, null=True)
    closed = models.BooleanField(default=False)

    def get_absolute_url(self):
        """Return the URL for this refund."""
        return reverse("orders:refund", kwargs={"pk": self.pk})

    def reason(self):
        """Return the reason for the refund."""
        return self._meta.verbose_name.title().replace(" Refund", "")


class RefundOut(Refund):
    """Model for refunds to customers."""

    contact_name = "Customer"


class RefundIn(Refund):
    """Model for refunds to us."""

    pass


class BreakageRefund(RefundOut):
    """Model for refunds lost in the post."""

    pass


class PackingMistakeRefund(RefundOut):
    """Model for refunds lost in the post."""

    pass


class LinkingMistakeRefund(RefundOut):
    """Model for refunds lost in the post."""

    pass


class LostInPostRefund(RefundIn):
    """Model for refunds lost in the post."""

    contact_name = "Logistics Partner"


class DemicRefund(RefundIn):
    """Model for refunds lost in the post."""

    contact_name = "Supplier"


class ProductRefund(models.Model):
    """Model for products requiring a refund."""

    refund = models.ForeignKey(
        Refund, on_delete=models.CASCADE, related_name="products"
    )
    product = models.ForeignKey(ProductSale, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
