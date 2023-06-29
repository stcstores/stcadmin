"""Models for the restock app."""
from django.core import validators
from django.db import models, transaction

from inventory.models import BaseProduct


class ReorderManager(models.Manager):
    """Manager for the Reorder model."""

    @transaction.atomic
    def set_count(self, product, count):
        """
        Set a reorder count for a product.

        Args:
            product: inventory.models.product.BaseProduct
            count: int
        """
        if count == 0:
            self.get(product=product).delete()
            return 0
        else:
            obj, _ = self.update_or_create(product=product, defaults={"count": count})
            obj.full_clean()
            obj.refresh_from_db
            return obj.count

    def set_comment(self, product, comment):
        """Set a reorder's comment field."""
        obj = self.get(product=product)
        obj.comment = comment
        obj.save()
        obj.full_clean()
        obj.refresh_from_db()
        return obj.comment


class Reorder(models.Model):
    """Model for re-order counts."""

    product = models.OneToOneField(
        BaseProduct,
        on_delete=models.CASCADE,
        related_name="reorder_count",
        verbose_name="Product",
        unique=True,
    )
    count = models.PositiveIntegerField(validators=[validators.MinValueValidator(1)])
    comment = models.TextField(blank=True, null=True)

    objects = ReorderManager()

    class Meta:
        """Meta class for the Reorder model."""

        verbose_name = "Reorder"
        verbose_name_plural = "Reorders"
