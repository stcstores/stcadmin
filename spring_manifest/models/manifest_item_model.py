"""Spring Item model for products on manifests."""

from ccapi import CCAPI
from django.db import models

from .manifest_package_model import ManifestPackage


class ManifestItem(models.Model):
    """Model for products in orders on manifests."""

    package = models.ForeignKey(ManifestPackage, on_delete=models.CASCADE)
    item_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    class Meta:
        """Meta class for ManifestItem."""

        verbose_name = 'Manifest Item'
        verbose_name_plural = 'Manifest Items'
        ordering = ('item_id', )

    def __str__(self):
        return '{}_{}'.format(str(self.package), self.item_id)

    def get_item(self):
        """Return product information."""
        return CCAPI.get_product(self.item_id)
