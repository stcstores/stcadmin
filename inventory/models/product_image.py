"""Models for storing product images."""

from django.db import models
from django.utils import timezone

from stcadmin import settings

from .product import BaseProduct, ProductRange


def get_storage():
    """Return the storage method for the ProductImage model."""
    if settings.DEBUG or settings.TESTING:
        return None
    else:
        return settings.ProductImageStorage


class ProductImage(models.Model):
    """Model for storing product images."""

    product_id = models.CharField(max_length=20)
    range_sku = models.CharField(max_length=20)
    sku = models.CharField(max_length=20)
    cloud_commerce_name = models.CharField(max_length=50)
    position = models.PositiveIntegerField()
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
    """Model for storing links between products and product images."""

    product = models.ForeignKey(
        BaseProduct, on_delete=models.CASCADE, related_name="images", editable=False
    )
    image = models.ForeignKey(
        ProductImage, on_delete=models.CASCADE, related_name="products", editable=False
    )
    ordering = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for the ProductImageLink model."""

        verbose_name = "Product Image Link"
        verbose_name_plural = "Product Image Links"
        ordering = ("ordering",)
        unique_together = ("product", "image")

    def __str__(self):
        return f"{self.product.sku} - {self.image}"


class ProductRangeImageLink(models.Model):
    """Model for storing links between product ranges and product images."""

    product_range = models.ForeignKey(
        ProductRange, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ForeignKey(
        ProductImage, on_delete=models.CASCADE, related_name="product_ranges"
    )
    ordering = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for the ProductRangeImageLink model."""

        verbose_name = "Product Range Image Link"
        verbose_name_plural = "Product Range Image Links"
        ordering = ("ordering",)
        unique_together = ("product_range", "image")

    def __str__(self):
        return f"{self.product_range.sku} - {self.image}"
