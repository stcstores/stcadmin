"""Model for FNAC product ranges."""

from django.db import models

from .category import Category


class FnacRangeManager(models.Manager):
    """Model manager for the FnacRange model."""

    def has_category(self):
        """Return a queryset of products with categories."""
        return self.get_queryset().filter(category__isnull=False)

    def missing_category(self):
        """Return a queryset of products without categories."""
        return self.get_queryset().filter(category__isnull=True)


class FnacRange(models.Model):
    """Model for FNAC product ranges."""

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True
    )

    objects = FnacRangeManager()

    def __str__(self):
        return f"{self.sku} - {self.name}"
