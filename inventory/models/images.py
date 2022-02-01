"""Models for storing product images."""

# from django.db import models


def product_image_path(instance, filename):
    """Return path to save product images."""
    return f"product_images/{instance.range_sku}/{instance.sku}/{filename}"


# class ProductImage(models.Model):
#     """Models for storing product images."""

#     product_id = models.CharField(max_length=20)
#     range_sku = models.CharField(max_length=20)
#     sku = models.CharField(max_length=20)
#     image_file = models.ImageField(upload_to=product_image_path)
