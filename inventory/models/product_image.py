"""Models for storing product images."""

import hashlib
from uuid import uuid4

from django.db import models
from django.utils import timezone
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import Anchor, ResizeCanvas, Thumbnail

from stcadmin import settings


def get_storage():
    """Return the storage method for the ProductImage model."""
    return settings.ProductImageStorage
    if settings.TESTING:
        return None
    else:
        return settings.ProductImageStorage


class SquareCrop:
    """Image processor for creating square images."""

    def process(self, img):
        """Return img as a square."""
        original_dimensions = img.size
        new_size = max(original_dimensions)
        img = ResizeCanvas(
            width=new_size,
            height=new_size,
            color=(255, 255, 255, 255),
            anchor=Anchor.CENTER,
        ).process(img)
        img = img.convert("RGB")
        return img


class SquareThumbnail:
    """Image processor for square thumbnails."""

    SIZE = 100

    def process(self, img):
        """Return img as a square thumbnail."""
        img = Thumbnail(
            width=self.SIZE, height=self.SIZE, crop=False, upscale=True
        ).process(img)
        img = SquareCrop().process(img)
        return img


class ProductImageManager(models.Manager):
    """Model manager for the ProductImage model."""

    def add_image(self, uploaded_file, hash_string=None):
        """Add an image to the database."""
        if hash_string is None:
            hash_string = self.get_hash(uploaded_file)
        uploaded_file.name = str(uuid4())
        image = self.model(hash=hash_string, image_file=uploaded_file)
        image.save()
        return image

    def get_or_add_image(self, uploaded_file):
        """Check if an image exists in the database and return or create it."""
        hash_string = self.get_hash(uploaded_file)
        try:
            return self.get(hash=hash_string)
        except self.model.DoesNotExist:
            return self.add_image(uploaded_file=uploaded_file, hash_string=hash_string)

    def get_hash(self, uploaded_file):
        """Return the has of an uploaded image."""
        ctx = hashlib.md5()
        if uploaded_file.multiple_chunks():
            for data in uploaded_file.chunks(2**20):
                ctx.update(data)
        else:
            ctx.update(uploaded_file.read())
        return ctx.hexdigest()


class ProductImage(models.Model):
    """Model for storing product images."""

    image_file = ProcessedImageField(
        storage=get_storage(),
        format="JPEG",
        options={"quality": 100},
    )
    square_image = ImageSpecField(
        source="image_file",
        processors=[SquareCrop()],
        format="JPEG",
        options={"quality": 80},
    )
    thumbnail = ImageSpecField(
        source="image_file",
        processors=[SquareThumbnail()],
        format="JPEG",
        options={"quality": 60},
    )
    hash = models.CharField(
        max_length=32, blank=True, null=True, unique=True, db_index=True
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)

    objects = ProductImageManager()

    class Meta:
        """Meta class for the ProductImage mode."""

        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

    def __str__(self):
        return self.image_file.name

    def delete(self, *args, **kwargs):
        """Delete image file from storage when deleting the object."""
        self.delete_square_image(silent=True)
        self.delete_thumbnail(silent=True)
        self.image_file.delete(silent=True)
        super().delete(*args, **kwargs)

    def delete_thumbnail(self, silent=False):
        """Delete the thumbnail image from storage."""
        try:
            self.thumbnail.storage.delete(self.thumbnail.name)
        except Exception:
            if silent is not False:
                raise

    def delete_square_image(self, silent=False):
        """Delete the square image from storage."""
        try:
            self.square_image.storage.delete(self.square_image.name)
        except Exception:
            if silent is not False:
                raise


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
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        """Meta class for ProductImageLink."""

        verbose_name = "Product Image Link"
        verbose_name_plural = "Product Image Links"
        ordering = ("position",)
        unique_together = [["product", "image"], ["product", "position"]]
