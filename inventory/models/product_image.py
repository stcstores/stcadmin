"""Model for product images."""
from ccapi import CCAPI
from django.db import models

from .products import Product


class ProductImage(models.Model):
    """Model for product images."""

    image_ID = models.CharField(max_length=20, unique=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    filename = models.CharField(max_length=200)
    URL = models.URLField()
    position = models.PositiveSmallIntegerField()

    class Meta:
        """Meta class for ProductImage."""

        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        ordering = ("position",)

    @classmethod
    def update_CC_image_order(cls, product):
        """Set the order of images for a product in Cloud Commerce."""
        images = cls.objects.filter(product=product).order_by("position")
        image_order = [image.image_ID for image in images]
        CCAPI.set_image_order(product_id=product.product_ID, image_ids=image_order)
