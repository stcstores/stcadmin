import os

from django.db import models


def get_product_image_upload_to(instance, filename):
    return os.path.join('product_images', instance.range_id, filename)


class STCAdminImage(models.Model):
    range_id = models.CharField(max_length=10)
    image = models.ImageField(upload_to=get_product_image_upload_to)
