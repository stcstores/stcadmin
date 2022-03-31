"""Models for storing product images."""

from django.db import models
from django.utils import timezone

from stcadmin import settings

from .managers import ActiveInactiveQueryset


def get_storage():
    """Return the storage method for the ProductImage model."""
    if settings.TESTING:
        return None
    else:
        return settings.ProductImageStorage


class BaseProductImage(models.Model):
    """Base class for product image fields."""

    ordering = models.PositiveIntegerField()
    image_file = models.ImageField(storage=get_storage())
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    objects = models.Manager.from_queryset(ActiveInactiveQueryset)()

    class Meta:
        """Meta class for BaseProductImage."""

        abstract = True

    def __str__(self):
        return self.image_file.name

    def delete(self, *args, **kwargs):
        """Delete image file from storage when deleting the object."""
        self.image_file.delete()
        super().delete(*args, **kwargs)


class ProductImage(BaseProductImage):
    """Model for storing product images."""

    product = models.ForeignKey(
        "BaseProduct",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="images",
    )

    class Meta:
        """Meta class for the ProductImage mode."""

        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ("ordering",)


class ProductRangeImage(BaseProductImage):
    """Model for storing product range images."""

    product_range = models.ForeignKey(
        "ProductRange",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="images",
    )

    class Meta:
        """Meta class for the ProductImage mode."""

        verbose_name = "Product Range Image"
        verbose_name_plural = "Product Range Images"
        ordering = ("ordering",)
