"""Model for refund tracking."""


from django.db import models
from django.shortcuts import reverse
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit
from polymorphic.models import PolymorphicModel

from .order import Order
from .product_sale import ProductSale


class Refund(PolymorphicModel):
    """Model for refund requests."""

    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    contact_contacted = models.BooleanField(default=False)
    refund_accepted = models.BooleanField(blank=True, null=True)
    refund_amount = models.PositiveIntegerField(blank=True, null=True)
    closed = models.BooleanField(default=False)

    def get_absolute_url(self):
        """Return the URL for this refund."""
        return reverse("orders:refund", kwargs={"pk": self.pk})

    def reason(self):
        """Return the reason for the refund."""
        return self._meta.verbose_name.title().replace(" Refund", "")


class RefundOut(Refund):
    """Model for refunds to customers."""

    contact_name = "Customer"


class RefundIn(Refund):
    """Model for refunds to us."""

    pass


class BreakageRefund(RefundOut):
    """Model for refunds lost in the post."""

    pass


class PackingMistakeRefund(RefundOut):
    """Model for refunds lost in the post."""

    pass


class LinkingMistakeRefund(RefundOut):
    """Model for refunds lost in the post."""

    pass


class LostInPostRefund(RefundIn):
    """Model for refunds lost in the post."""

    contact_name = "Logistics Partner"


class DemicRefund(RefundIn):
    """Model for refunds lost in the post."""

    contact_name = "Supplier"


class ProductRefund(models.Model):
    """Model for products requiring a refund."""

    refund = models.ForeignKey(
        Refund, on_delete=models.CASCADE, related_name="products"
    )
    product = models.ForeignKey(ProductSale, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)


def image_path(instance, filename):
    """Return the path to which refund images will be saved."""
    path = f"refunds/images/{instance.refund.id}/"
    if instance.product_refund is not None:
        path += f"{instance.product_refund.id}/"
    path += filename
    return path


def thumb_path(instance, filename):
    """Return the path to which refund images will be saved."""
    path = f"refunds/thumbs/{instance.refund.id}/"
    if instance.product_refund is not None:
        path += f"{instance.product_refund.id}/"
    path += filename
    return path


class RefundImage(models.Model):
    """Model for images of refunds."""

    THUMB_SIZE = 200

    refund = models.ForeignKey(Refund, on_delete=models.CASCADE)
    product_refund = models.ForeignKey(
        ProductRefund, blank=True, null=True, on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to=image_path, height_field="image_height", width_field="image_width"
    )
    thumbnail = ProcessedImageField(
        upload_to=thumb_path,
        processors=[ResizeToFit(THUMB_SIZE, THUMB_SIZE)],
        format="JPEG",
        options={"quality": 60},
        height_field="thumb_height",
        width_field="thumb_width",
    )
    image_height = models.PositiveIntegerField()
    image_width = models.PositiveIntegerField()
    thumb_height = models.PositiveIntegerField()
    thumb_width = models.PositiveIntegerField()
