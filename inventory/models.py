import os
import uuid

from django.db import models


def get_product_image_upload_to(instance, original_filename):
    extension = original_filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4(), extension)
    return os.path.join('product_images', instance.range_id, filename)


class STCAdminImage(models.Model):
    range_id = models.CharField(max_length=10)
    image = models.ImageField(upload_to=get_product_image_upload_to)

    def delete(self, *args, **kwargs):
        image_path = self.image.path
        range_dir = os.path.dirname(image_path)
        if os.path.isfile(self.image.path):
            os.remove(self.image.path)
        if not os.listdir(range_dir):
            os.rmdir(range_dir)
        super(models.Model).delete(*args, **kwargs)
