"""Models for storing product images."""

from django.db import models

from stcadmin import settings


def get_storage():
    """Return the storage method for the ProductImage model."""
    if settings.DEBUG or settings.TESTING:
        return None
    else:
        return settings.ProductImageStorage


class ProductImage(models.Model):
    """Models for storing product images."""

    product_id = models.CharField(max_length=20)
    range_sku = models.CharField(max_length=20)
    sku = models.CharField(max_length=20)
    cloud_commerce_name = models.CharField(max_length=50)
    position = models.PositiveIntegerField()
    image_file = models.ImageField(storage=get_storage())

    def delete(self, *args, **kwargs):
        """Delete image file from storage when deleting the object."""
        self.image_file.delete()
        super().delete(*args, **kwargs)
