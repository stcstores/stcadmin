"""Models for the order app."""

from ccapi import CCAPI
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from inventory.models import Supplier
from shipping.models import VATRate


class ProductSale(models.Model):
    """Model for product sales."""

    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    product_ID = models.CharField(max_length=25)
    sku = models.CharField(max_length=25, null=True)
    name = models.TextField(null=True)
    weight = models.PositiveIntegerField(null=True)
    quantity = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()
    supplier = models.ForeignKey(
        Supplier, blank=True, null=True, on_delete=models.PROTECT
    )
    purchase_price = models.PositiveIntegerField(blank=True, null=True)
    vat_rate = models.PositiveSmallIntegerField(blank=True, null=True)
    end_of_line = models.BooleanField(blank=True, null=True)
    details_success = models.BooleanField(blank=True, null=True)

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
            except ObjectDoesNotExist as e:
                self.details_success = False
                self.save()
                raise e
            except Exception as e:
                exception = e
                continue
            break
        else:
            self.details_success = False
            self.save()
            raise exception
        self.details_success = True
        self.save()

    def _update_details(self):
        product = CCAPI.get_product(self.product_ID)
        self.vat_rate = VATRate.objects.get(cc_id=product.vat_rate_id).percentage
        self.supplier = Supplier.objects.get(
            product_option_value_ID=str(product.options["Supplier"].value.id)
        )
        self.purchase_price = int(
            float(product.options["Purchase Price"].value.value) * 100
        )
        self.end_of_line = bool(product.end_of_line)
        self.save()

    def total_weight(self):
        """Return the combined weight of this item."""
        return self.weight * self.quantity

    def _price_paid(self):
        return self.price * self.quantity

    def _vat_paid(self):
        if self.order.channel.include_vat is False:
            return 0
        if self.order.country.vat_is_required() == self.order.country.VAT_NEVER:
            return 0
        if self.order.country.vat_is_required() == self.order.country.VAT_ALWAYS:
            vat_rate = self.order.country.vat_rate()
        if self.order.country.vat_is_required() == self.order.country.VAT_VARIABLE:
            vat_rate = self.vat_rate
        vat_divisor = 1 + (vat_rate / 100)
        return int(((self._price_paid() / vat_divisor) - self._price_paid()) * -1)

    def _channel_fee_paid(self):
        channel_fee = self.order.channel.channel_fee
        return int(float(self._price_paid() / 100) * channel_fee)

    def _purchase_price_total(self):
        return self.purchase_price * self.quantity
