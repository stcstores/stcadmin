"""Models for the Purhcases app."""

from django.contrib.auth import get_user_model
from django.db import models
from polymorphic.models import PolymorphicModel

from shipping.models import ShippingPrice


class Purchase(PolymorphicModel):
    """Base model for purchases."""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    to_pay = models.IntegerField()
    paid = models.BooleanField(default=False)


class StockPurchase(Purchase):
    """Model for stock purchases."""

    product_id = models.CharField(max_length=20)
    product_sku = models.CharField(max_length=20)
    product_name = models.CharField(max_length=255)
    product_purchase_price = models.IntegerField()
    quantity = models.IntegerField()


class ShippingPurchase(Purchase):
    """Model for shipping purchaes."""

    shipping_price = models.ForeignKey(ShippingPrice, on_delete=models.PROTECT)
