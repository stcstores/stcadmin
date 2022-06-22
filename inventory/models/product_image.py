"""Models for storing product images."""

from django.db import models
from django.utils import timezone

from stcadmin import settings


def get_storage():
    """Return the storage method for the ProductImage model."""
    return settings.ProductImageStorage
    if settings.TESTING:
        return None
    else:
        return settings.ProductImageStorage


class ProductImage(models.Model):
    """Model for storing product images."""

    image_file = models.ImageField(storage=get_storage())

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for the ProductImage mode."""

        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

    def __str__(self):
        return self.image_file.name

    def delete(self, *args, **kwargs):
        """Delete image file from storage when deleting the object."""
        self.image_file.delete()
        super().delete(*args, **kwargs)


class ProductImageLink(models.Model):
    """Model for managing links between products and images."""

    product = models.ForeignKey(
        "BaseProduct",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="product_image_links",
    )
    image = models.ForeignKey(
        ProductImage,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="product_image_links",
    )
    position = models.PositiveIntegerField(default=0)
