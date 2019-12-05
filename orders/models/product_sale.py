"""Models for the order app."""

from django.db import models


class ProductSale(models.Model):
    """Model for product sales."""

    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    product_ID = models.CharField(max_length=25)
    quantity = models.PositiveSmallIntegerField()
    price = models.PositiveSmallIntegerField()

    class Meta:
        """Meta class for the ProductSale model."""

        verbose_name = "Product Sale"
        verbose_name_plural = "Product Sales"
        unique_together = ("order", "product_ID")
