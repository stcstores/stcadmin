"""Models for the restock app."""
from django.core import validators
from django.db import models, transaction
from django.utils import timezone

from inventory.models import BaseProduct


class ReorderQuerySet(models.QuerySet):
    """Queryset for reorders."""

    def open(self):
        """Return a queryset of open reorders."""
        return self.filter(closed_at__isnull=True)

    def closed(self):
        """Return a queryset of historic reorders."""
        return self.filter(closed_at__isnull=False)


class ReorderManager(models.Manager):
    """Manager for the Reorder model."""

    queryset_class = ReorderQuerySet

    @transaction.atomic
    def set_count(self, product, count):
        """
        Set a reorder count for a product.

        Args:
            product: inventory.models.product.BaseProduct
            count: int
        """
        if count == 0:
            self.open().get(product=product).close()
            return 0
        else:
            obj, _ = self.update_or_create(
                product=product, closed_at=None, defaults={"count": count}
            )
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

    def last_reorder(self, product):
        """Return the most recent reorder for a product."""
        try:
            return self.filter(product=product).closed().latest("closed_at")
        except Reorder.DoesNotExist:
            return None


class Reorder(models.Model):
    """Model for re-order counts."""

    product = models.ForeignKey(
        BaseProduct,
        on_delete=models.CASCADE,
        related_name="reorders",
        verbose_name="Product",
    )
    count = models.PositiveIntegerField(validators=[validators.MinValueValidator(1)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    objects = ReorderManager.from_queryset(ReorderQuerySet)()

    class Meta:
        """Meta class for the Reorder model."""

        verbose_name = "Reorder"
        verbose_name_plural = "Reorders"

    def close(self):
        """Mark the reorder as closed."""
        self.closed_at = timezone.now()
        self.save()
