"""Models for the Purhcases app."""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from polymorphic.models import PolymorphicModel

from shipping.models import ShippingPrice


class Purchase(PolymorphicModel):
    """Base model for purchases."""

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="purchaser"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="purchase_creator"
    )
    modified_at = models.DateTimeField(auto_now=True)
    to_pay = models.IntegerField()
    cancelled = models.BooleanField(default=False)


class StockPurchase(Purchase):
    """Model for stock purchases."""

    product_id = models.CharField(max_length=20)
    product_sku = models.CharField(max_length=20)
    product_name = models.CharField(max_length=255)
    full_price = models.IntegerField()
    discount_percentage = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(0), MaxValueValidator(100))
    )
    quantity = models.IntegerField()


class ShippingPurchase(Purchase):
    """Model for shipping purchaes."""

    shipping_price = models.ForeignKey(ShippingPrice, on_delete=models.PROTECT)


class PurchaseNote(Purchase):
    """Model for purchase notes."""

    text = models.TextField()
