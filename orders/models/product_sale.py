"""Models for the order app."""

from ccapi import CCAPI
from django.db import models

from inventory.models import Department
from shipping.models import VATRate


class ProductSaleManager(models.Manager):
    """Model manager for the ProductSale model."""

    def update_product_details(self):
        """Update missing product details."""
        for product_sale in self.filter(error=None):
            try:
                product_sale.update_details()
            except Exception:
                pass


class ProductSale(models.Model):
    """Model for product sales."""

    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    product_ID = models.CharField(max_length=25)
    sku = models.CharField(max_length=25, null=True)
    name = models.TextField(null=True)
    weight = models.PositiveIntegerField(null=True)
    quantity = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()
    department = models.ForeignKey(
        Department, blank=True, null=True, on_delete=models.PROTECT
    )
    purchase_price = models.PositiveIntegerField(blank=True, null=True)
    vat_rate = models.PositiveSmallIntegerField(blank=True, null=True)
    error = models.BooleanField(blank=True, null=True)

    objects = ProductSaleManager()

    class Meta:
        """Meta class for the ProductSale model."""

        verbose_name = "Product Sale"
        verbose_name_plural = "Product Sales"
        unique_together = ("order", "product_ID")

    def update_details(self):
        """Set the product's department, VAT rate and purchase price."""
        exception = None
        for attempt in range(10):
            try:
                self._update_details()
            except Exception as e:
                exception = e
                continue
            break
        else:
            self.error = True
            self.save()
            raise exception
        self.error = False
        self.save()

    def _update_details(self):
        product = CCAPI.get_product(self.product_ID)
        self.vat_rate = VATRate.objects.get(cc_id=product.vat_rate_id).percentage
        self.department = Department.objects.get(
            product_option_value_ID=product.options["Department"].id
        )
        self.purchase_price = int(product.options["Purchase Price"].value * 100)
        self.save()
