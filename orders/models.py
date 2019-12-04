"""Models for the order app."""
import pytz
from django.db import models
from django.utils.timezone import make_aware

from print_audit.models import CloudCommerceUser
from shipping.models import Country, Service, ShippingRule


class Channel(models.Model):
    """Model for sales channels."""

    name = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        """Meta class for the Channel model."""

        verbose_name = "Channel"
        verbose_name_plural = "Channels"


class Order(models.Model):
    """Model for Cloud Commerce Orders."""

    TIME_ZONE = "Europe/London"

    order_ID = models.CharField(max_length=12, unique=True, db_index=True)
    customer_ID = models.CharField(max_length=12, blank=True, null=True)
    recieved = models.DateTimeField()
    dispatched = models.DateTimeField(blank=True, null=True)
    cancelled = models.BooleanField(default=False)
    channel = models.ForeignKey(
        Channel, blank=True, null=True, on_delete=models.PROTECT
    )
    channel_order_ID = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(
        Country, blank=True, null=True, on_delete=models.PROTECT
    )
    shipping_rule = models.ForeignKey(
        ShippingRule, blank=True, null=True, on_delete=models.PROTECT
    )
    shipping_service = models.ForeignKey(
        Service, blank=True, null=True, on_delete=models.PROTECT
    )

    class Meta:
        """Meta class for the Order model."""

        verbose_name = "Order"
        verbose_name_plural = "Orders"

    @staticmethod
    def is_naive(datetime):
        """Return True if datetime is naive, otherwise return False."""
        return datetime.tzinfo is None or datetime.tzinfo.utcoffset(datetime) is None

    def make_tz_aware(self, datetime):
        """Make a naive datetime timezone aware."""
        return make_aware(datetime, timezone=pytz.timezone(self.TIME_ZONE))

    def save(self, *args, **kwargs):
        """Make datetime fields timezone aware."""
        if self.is_naive(self.recieved):
            self.recieved = self.make_tz_aware(self.recieved)
        if self.dispatched is not None and self.is_naive(self.dispatched):
            self.dispatched = self.make_tz_aware(self.dispatched)
        super().save(*args, **kwargs)


class ProductSale(models.Model):
    """Model for product sales."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_ID = models.CharField(max_length=25)
    quantity = models.PositiveSmallIntegerField()
    price = models.PositiveSmallIntegerField()

    class Meta:
        """Meta class for the ProductSale model."""

        verbose_name = "Product Sale"
        verbose_name_plural = "Product Sales"
        unique_together = ("order", "product_ID")


class PackingRecord(models.Model):
    """Model for order packing."""

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    packed_by = models.ForeignKey(CloudCommerceUser, on_delete=models.PROTECT)

    class Meta:
        """Meta class for the Packing model."""

        verbose_name = "Packing Record"
        verbose_name_plural = "Packing Records"
