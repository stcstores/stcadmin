"""Model for storing records of item breakages."""
from django.db import models
from django.utils import timezone

from home.models import CloudCommerceUser


class Breakage(models.Model):
    """Model for storing details of product breakages."""

    product_sku = models.CharField(max_length=20)
    order_id = models.CharField(max_length=10)
    note = models.TextField(blank=True, null=True)
    packer = models.ForeignKey(CloudCommerceUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        """Meta class for UserFeedback."""

        verbose_name = "Breakage"
        verbose_name_plural = "Breakages"
        ordering = ("timestamp",)

    def __str__(self):
        return "{} on order {}".format(self.product_sku, self.order_id)