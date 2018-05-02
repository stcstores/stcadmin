"""Spring Item model for products on manifests."""

from ccapi import CCAPI
from django.db import models

from .spring_package_model import SpringPackage


class SpringItem(models.Model):
    """Model for products in orders on manifests."""

    class Meta:
        """Order by item ID."""

        ordering = ('item_id', )

    package = models.ForeignKey(SpringPackage, on_delete=models.CASCADE)
    item_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return '{}_{}'.format(str(self.package), self.item_id)

    def get_item(self):
        """Return product information."""
        return CCAPI.get_product(self.item_id)
