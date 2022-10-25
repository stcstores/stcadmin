"""Models for storing product images."""

import hashlib
from uuid import uuid4

from django.db import models, transaction
from django.db.models import Max
from django.utils import timezone
from imagekit.cachefiles.strategies import Optimistic
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import Anchor, ResizeCanvas, Thumbnail

from stcadmin import settings


def get_storage():
    """Return the storage method for the ProductImage model."""
    # return settings.ProductImageStorage
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
        cachefile_strategy=Optimistic,
    )
    thumbnail = ImageSpecField(
        source="image_file",
        processors=[SquareThumbnail()],
        format="JPEG",
        options={"quality": 60},
        cachefile_strategy=Optimistic,
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
        self.image_file.delete()
        return super().delete(*args, **kwargs)

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


class BaseImageLinkManager(models.Manager):
    """Base manager for image link models."""

    def get_highest_image_position(self, product_id):
        """
        Return the highest position number for a product's images or None if no images exist.

        Args:
            product_id (int): The product's PK.

        Returns:
            int or None: The highest image position for the product's images or None if
                the product has no images.
        """
        kwargs = {self.product_field + "__pk": product_id}
        return self.filter(**kwargs).aggregate(Max("position"))["position__max"]

    @transaction.atomic
    def set_image_order(self, product_pk, image_order):
        """Update the order of product imges.

        Args:
            product_pk (int): The PK of the product.
            image_order (list[int]): The IDs of the product's images in the new order.

        Raises:
            Exception: _description_
        """
        image_links = self._get_image_links(product_pk)
        if not set(image_links.values_list("image__pk", flat=True)) == set(image_order):
            raise Exception("Did not get expected image IDs.")
        for link in image_links:
            link.position = image_order.index(link.image.pk)
            link.save()

    @transaction.atomic
    def normalize_image_positions(self, product_pk):
        """Make image positions continuous from zero."""
        links = self._get_image_links(product_pk).order_by("position")
        for i, link in enumerate(links):
            if link.position != i:
                link.position = i
                link.save()

    def _get_image_links(self, product_pk):
        return self.filter(**{self.product_field + "__pk": product_pk})


class ProductImageLinkManager(BaseImageLinkManager):
    """Manager for the ProductImageLink model."""

    product_field = "product"

    @transaction.atomic
    def add_images(self, products, uploaded_images):
        """Add one or more images to one or more products.

        Args:
            products (iterable[inventory.models.Product]): List of products.
            uploaded_images (iterable[django.core.files.uploadedfile.InMemoryUploadedFile]):
                List of images
        """
        for image in uploaded_images:
            db_image = ProductImage.objects.get_or_add_image(image)
            for i, product in enumerate(products, 1):
                highest_position = self.get_highest_image_position(product.pk)
                if highest_position is None:
                    highest_position = -1
                self.model(
                    product=product, image=db_image, position=highest_position + i
                ).save()
            self.normalize_image_positions(product.pk)


class ProductRangeImageLinkManager(BaseImageLinkManager):
    """Manager for the ProductRangeImageLink model."""

    product_field = "product_range"

    @transaction.atomic
    def add_images(self, product_range, uploaded_images):
        """Add images to a product range.

        Args:
            product_range (inventory.models.ProductRange): The product range to add
                images too.
            uploaded_images (iterable[django.core.files.uploadedfile.InMemoryUploadedFile]):
                The images to add.
        """
        for image in uploaded_images:
            db_image = ProductImage.objects.get_or_add_image(image)
            highest_position = self.get_highest_image_position(product_range.pk)
            if highest_position is None:
                highest_position = -1
            self.model(
                product_range=product_range,
                image=db_image,
                position=highest_position + 1,
            ).save()


class BaseImageLink(models.Model):
    """Base model for links between products and images."""

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    modified_at = models.DateTimeField(auto_now=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        """Meta class for BaseImageLink."""

        abstract = True


class ProductImageLink(BaseImageLink):
    """Model for managing links between products and images."""

    product = models.ForeignKey(
        "BaseProduct",
        on_delete=models.CASCADE,
        related_name="product_image_links",
    )
    image = models.ForeignKey(
        ProductImage,
        on_delete=models.CASCADE,
        related_name="product_image_links",
    )

    objects = ProductImageLinkManager()

    class Meta:
        """Meta class for ProductImageLink."""

        verbose_name = "Product Image Link"
        verbose_name_plural = "Product Image Links"
        ordering = ("position",)
        unique_together = [["product", "image"]]


class ProductRangeImageLink(BaseImageLink):
    """Model for managing links between product ranges and images."""

    product_range = models.ForeignKey(
        "ProductRange",
        on_delete=models.CASCADE,
        related_name="product_range_image_links",
    )
    image = models.ForeignKey(
        ProductImage,
        on_delete=models.CASCADE,
        related_name="product_range_image_links",
    )

    objects = ProductRangeImageLinkManager()

    class Meta:
        """Meta class for ProductRangeImageLink."""

        verbose_name = "Product Range Image Link"
        verbose_name_plural = "Product Range Image Links"
        ordering = ("position",)
        unique_together = [["product_range", "image"]]
