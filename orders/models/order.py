"""The Order model."""
import csv
import io
from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone

from home.models import Staff
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

    packed_by = models.ForeignKey(
        Staff,
        on_delete=models.PROTECT,
        related_name="packed_orders",
        blank=True,
        null=True,
    )

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
        try:
            return int((self.profit() / self.total_paid_GBP) * 100)
        except ZeroDivisionError:
            return 0

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


class OrderExporter:
    """Export order details."""

    ORDER_ID = "Order ID"
    DATE_RECIEVED = "Date Recieved"
    DATE_DISPATCHED = "Date Dispatched"
    COUNTRY = "Country"
    CHANNEL = "Channel"
    TRACKING_NUMBER = "Tracking Number"
    SHIPPING_SERVICE = "Shipping Service"
    CURRENCY = "Currency"
    TOTAL_PAID = "Total Paid"
    TOTAL_PAID_GBP = "Total Paid (GBP)"
    WEIGHT = "Weight"
    CHANNEL_FEE = "Channel Fee"
    PURCHASE_PRICE = "Purchase Price"
    PROFIT = "Profit"
    PROFIT_PERCENTAGE = "Profit Percentage"

    header = [
        ORDER_ID,
        DATE_RECIEVED,
        DATE_DISPATCHED,
        COUNTRY,
        CHANNEL,
        TRACKING_NUMBER,
        SHIPPING_SERVICE,
        CURRENCY,
        TOTAL_PAID,
        TOTAL_PAID_GBP,
        WEIGHT,
        CHANNEL_FEE,
        PURCHASE_PRICE,
        PROFIT,
        PROFIT_PERCENTAGE,
    ]

    def make_row(self, order):
        """Return a row of order data."""
        return {
            self.ORDER_ID: order.order_id,
            self.DATE_RECIEVED: self.format_date(order.recieved_at),
            self.DATE_DISPATCHED: self._order_dispatched_value(order),
            self.COUNTRY: order.country.name,
            self.CHANNEL: order.channel.name if order.channel else None,
            self.TRACKING_NUMBER: order.tracking_number,
            self.SHIPPING_SERVICE: self._shipping_service_value(order),
            self.CURRENCY: order.currency.code if order.currency else None,
            self.TOTAL_PAID: self.format_currency(order.total_paid),
            self.TOTAL_PAID_GBP: self.format_currency(order.total_paid_GBP),
            self.WEIGHT: order.total_weight(),
            self.CHANNEL_FEE: self._channel_fee_value(order),
            self.PURCHASE_PRICE: self._purchase_price_value(order),
            self.PROFIT: self._profit_value(order),
            self.PROFIT_PERCENTAGE: self._profit_percentage_value(order),
        }

    def _order_dispatched_value(self, order):
        if order.is_dispatched():
            return order.dispatched_at.strftime("%Y-%m-%d")
        else:
            return "UNDISPATCHED"

    def _channel_fee_value(self, order):
        try:
            return self.format_currency(order.channel_fee_paid())
        except Exception:
            return ""

    def _purchase_price_value(self, order):
        try:
            return self.format_currency(order.purchase_price())
        except Exception:
            return ""

    def _shipping_service_value(self, order):
        if order.shipping_service is None:
            return None
        else:
            return order.shipping_service.name

    def _profit_value(self, order):
        if order.calculated_shipping_price is None:
            return None
        return self.format_currency(order.profit())

    def _profit_percentage_value(self, order):
        if order.calculated_shipping_price is None:
            return None
        return order.profit_percentage()

    @staticmethod
    def format_date(date):
        """Return a date formatted as a string."""
        return date.strftime("%Y-%m-%d")

    def format_currency(self, price):
        """Return a price as a formatted string."""
        if price is None:
            return None
        return f"{price / 100:.2f}"

    def make_csv(self, orders):
        """Return the export as a CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.header)
        for order in orders:
            row_data = self.make_row(order)
            row = [row_data.get(col, "") for col in self.header]
            writer.writerow(row)
        return output.getvalue()
