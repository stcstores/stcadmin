import os
import uuid

from django.db import models


def get_product_image_upload_to(instance, original_filename):
    extension = original_filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4(), extension)
    return os.path.join('product_images', str(instance.range_id), filename)


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
        super(STCAdminImage, self).delete(*args, **kwargs)


class Barcode(models.Model):
    barcode = models.CharField(max_length=13, unique=True)
    used = models.BooleanField(default=False)

    def mark_used(self):
        self.used = True
        self.save()


def get_barcode():
    barcode = Barcode.objects.filter(used=False).all()[0]
    barcode.used = True
    barcode.save()
    return barcode.barcode
