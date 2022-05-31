"""The Order model."""
from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone

from shipping.models import Country, Currency, ShippingPrice, ShippingService

from .channel import Channel


def urgent_since():
    """Return the date after which undispatched orders are urgent."""
    day_offsets = {0: 3, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 2}
    now = timezone.now()
    urgent_cutoff = datetime.combine(
        (now - timedelta(days=day_offsets[now.weekday()])).date(), datetime.min.time()
    )
    return timezone.make_aware(urgent_cutoff)


class OrderQueryset(models.QuerySet):
    """Model manager for order.Order."""

    def dispatched(self):
        """Return a queryset of dispatched orders."""
        return self.filter(dispatched_at__isnull=False)

    def undispatched(self):
        """Return a queryset of undispatched orders."""
        return self.filter(dispatched_at__isnull=True, cancelled=False, ignored=False)

    def priority(self):
        """Return a queryset of priority orders."""
        return self.filter(shipping_service__priority=True, cancelled=False)

    def non_priority(self):
        """Return a queryset of non-priority orders."""
        return self.filter(shipping_service__priority=False, cancelled=False)

    def urgent(self):
        """Return a queryset of urgent orders."""
        return self.undispatched().filter(recieved_at__lte=urgent_since())


class Order(models.Model):
    """Model for Cloud Commerce Orders."""

    DISPATCH_EPOCH = datetime(2000, 1, 1, 0, 0)

    order_id = models.CharField(max_length=12, unique=True, db_index=True)
    recieved_at = models.DateTimeField()
    dispatched_at = models.DateTimeField(blank=True, null=True)
    cancelled = models.BooleanField(default=False)
    ignored = models.BooleanField(default=False)
    channel = models.ForeignKey(
        Channel,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        limit_choices_to={"active": True},
    )
    external_reference = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(
        Country, blank=True, null=True, on_delete=models.PROTECT
    )
    shipping_service = models.ForeignKey(
        ShippingService,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        limit_choices_to={"active": True},
    )
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    priority = models.BooleanField(default=False)

    displayed_shipping_price = models.PositiveIntegerField(blank=True, null=True)
    calculated_shipping_price = models.PositiveIntegerField(blank=True, null=True)

    tax = models.PositiveIntegerField(blank=True, null=True)

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="order_currencies",
        blank=True,
        null=True,
    )
    total_paid = models.PositiveIntegerField(blank=True, null=True)
    total_paid_GBP = models.PositiveIntegerField(blank=True, null=True)

    objects = models.Manager.from_queryset(OrderQueryset)()

    class Meta:
        """Meta class for the Order model."""

        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order: {self.order_id}"

    def is_dispatched(self):
        """Return True if the order is dispatched, otherwise return False."""
        return self.dispatched_at is not None

    def total_weight(self):
        """Return the combined weight of the order."""
        return sum((sale.total_weight() for sale in self.productsale_set.all()))

    def channel_fee_paid(self):
        """Return the channel fee for the order."""
        return sum((sale._channel_fee_paid() for sale in self.productsale_set.all()))

    def purchase_price(self):
        """Return the combined purchase price of the order."""
        return sum(
            (sale._purchase_price_total() for sale in self.productsale_set.all())
        )

    def item_count(self):
        """Return the number of items included in the order."""
        return sum((sale.quantity for sale in self.productsale_set.all()))

    def profit(self):
        """Return the profit made on the order."""
        expenses = sum(
            (
                self.tax,
                self.channel_fee_paid(),
                self.purchase_price(),
                self.calculated_shipping_price,
            )
        )
        return self.total_paid_GBP - expenses

    def profit_percentage(self):
        """Return the percentage of the amount paid for the order that is profit."""
        return int((self.profit() / self.total_paid_GBP) * 100)

    def calculate_shipping_price(self):
        """Return the shipping price for this order based on current shipping prices."""
        shipping_price = ShippingPrice.objects.find_shipping_price(
            country=self.country, shipping_service=self.shipping_service
        )
        return shipping_price.price(self.total_weight())

    def _set_calculated_shipping_price(self):
        """Update calculated shipping_price with current price calculatrion."""
        self.calculated_shipping_price = self.calculate_shipping_price()
        self.save()

    def packed_by(self):
        """Return the packer who packed this order."""
        try:
            return self.packingrecord.packed_by
        except Exception:
            return None
