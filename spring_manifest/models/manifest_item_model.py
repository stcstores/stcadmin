"""SpringOrder model for products on manifests."""

from ccapi import CCAPI
from django.db import models

from .manifest_package_model import ManifestPackage


class ManifestItem(models.Model):
    """Model for products in orders on manifests."""

    name = models.CharField(max_length=255, default="?")
    full_name = models.CharField(max_length=255, default="?")
    package = models.ForeignKey(ManifestPackage, on_delete=models.CASCADE)
    item_id = models.PositiveIntegerField()
    weight = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField()

    class Meta:
        """Meta class for ManifestItem."""

        verbose_name = "Manifest Item"
        verbose_name_plural = "Manifest Items"
        ordering = ("item_id",)

    def __str__(self):
        return "{}_{}".format(str(self.package), self.item_id)

    def get_item(self):
        """Return product information."""
        return CCAPI.get_product(self.item_id)
