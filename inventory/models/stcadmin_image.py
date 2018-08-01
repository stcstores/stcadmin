"""
STCAdmin Image model.

Store an image for a Cloud Commerce Product Range outside of Cloud Commerce.
"""

import os
import uuid

from django.db import models


def get_product_image_upload_to(instance, original_filename):
    """Return save location for STCAdminImage.image files."""
    extension = original_filename.split(".")[-1]
    filename = "{}.{}".format(uuid.uuid4(), extension)
    return os.path.join("product_images", str(instance.range_id), filename)


class STCAdminImage(models.Model):
    """Store an image associated with a Cloud Commerce Product Range."""

    range_id = models.CharField(max_length=10)
    image = models.ImageField(upload_to=get_product_image_upload_to)

    class Meta:
        """Meta class for STCAdminImage."""

        verbose_name = "STC Admin Image"
        verbose_name_plural = "STC Admin Images"

    def delete(self, *args, **kwargs):
        """Delete file when object is deleted."""
        image_path = self.image.path
        range_dir = os.path.dirname(image_path)
        if os.path.isfile(self.image.path):
            os.remove(self.image.path)
        if not os.listdir(range_dir):
            os.rmdir(range_dir)
        super(STCAdminImage, self).delete(*args, **kwargs)
