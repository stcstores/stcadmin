"""Models for the Suppliers app."""

from django.db import models
from django.urls import reverse


class Supplier(models.Model):
    """Stores suppliers of products."""

    name = models.CharField(max_length=200, unique=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)

    def get_absolute_url(self):
        """Return URL for supplier."""
        return reverse(
            'suppliers:supplier', kwargs={'pk': str(self.id)})

    def __str__(self):
        return self.name


class StockItem(models.Model):
    """Stores details of products."""

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product_code = models.CharField(max_length=200, unique=True)
    supplier_title = models.CharField(max_length=200)
    box_quantity = models.PositiveSmallIntegerField(blank=True, null=True)
    linnworks_title = models.CharField(max_length=200, null=True, blank=True)
    linnworks_sku = models.CharField(max_length=200, null=True, blank=True)
    notes = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.linnworks_title
