"""Models for Stock Check app."""

from django.db import models
from inventory.models import Bay


class Product(models.Model):
    """The Product models stores Cloud Commerce Products."""

    range_id = models.PositiveIntegerField(
        verbose_name='Range ID', primary_key=False, null=True, blank=True)
    product_id = models.PositiveIntegerField(
        verbose_name='Product ID', primary_key=False, unique=True,
        db_index=True, null=True, blank=True)
    sku = models.CharField(max_length=50, db_index=True, unique=True)
    bays = models.ManyToManyField(Bay, through='ProductBay')

    class Meta:
        """Meta class for Product."""

        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def bay_names(self):
        """Return list of bay names as a string."""
        return ', '.join([str(bay) for bay in self.bays.all()])

    def __str__(self):
        return self.sku


class ProductBay(models.Model):
    """THe ProductBay model stores the quantity of a product in a Bay."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bay = models.ForeignKey(Bay, on_delete=models.CASCADE)
    stock_level = models.PositiveIntegerField(
        blank=True, null=True, default=None)

    class Meta:
        """Meta class for ProductBay."""

        verbose_name = 'Product Bay'
        verbose_name_plural = 'Product Bays'
