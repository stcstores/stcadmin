"""The Order model."""
from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone

from shipping.models import Country, CourierService, ShippingPrice, ShippingRule

from .channel import Channel


class CountryNotRecognisedError(ValueError):
    """Exception raised when a country cannot be found by country ID."""

    def __init__(self, country_code, order_ID):
        """Raise exception."""
        exception_string = (
            f"Country code {country_code} from order {order_ID} does not exist."
        )
        super().__init__(exception_string)


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
        return self.filter(shipping_rule__priority=True, cancelled=False)

    def non_priority(self):
        """Return a queryset of non-priority orders."""
        return self.filter(shipping_rule__priority=False, cancelled=False)

    def urgent(self):
        """Return a queryset of urgent orders."""
        return self.undispatched().filter(recieved_at__lte=urgent_since())

    def profit_calculable(self):
        """Return a queryset of products with all required information for profit calculations."""
        return (
            self.dispatched()
            .filter(postage_price_success=True)
            .exclude(productsale__details_success__isnull=True)
            .exclude(productsale__details_success=False)
        )


class OrderManager(models.Manager):
    """Model manager for orders.Order."""

    def update_postage_prices(self):
        """Add postage prices to orders."""
        for order in self.dispatched().filter(
            postage_price__isnull=True,
            postage_price_success__isnull=True,
            shipping_rule__isnull=False,
        ):
            try:
                order._set_postage_price()
            except Exception as e:
                raise Exception(
                    f"Error finding postage price for order {order.order_ID}: {e}"
                )


class Order(models.Model):
    """Model for Cloud Commerce Orders."""

    DISPATCH_EPOCH = datetime(2000, 1, 1, 0, 0)

    order_ID = models.CharField(max_length=12, unique=True, db_index=True)
    customer_ID = models.CharField(max_length=12, blank=True, null=True)
    recieved_at = models.DateTimeField()
    dispatched_at = models.DateTimeField(blank=True, null=True)
    cancelled = models.BooleanField(default=False)
    ignored = models.BooleanField(default=False)
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
    courier_service = models.ForeignKey(
        CourierService, blank=True, null=True, on_delete=models.PROTECT
    )
    tracking_number = models.CharField(max_length=255, blank=True, null=True)
    total_paid = models.PositiveIntegerField(blank=True, null=True)
    total_paid_GBP = models.PositiveIntegerField(blank=True, null=True)
    priority = models.BooleanField(default=False)
    postage_price = models.PositiveIntegerField(blank=True, null=True)
    postage_price_success = models.BooleanField(blank=True, null=True)

    CountryNotRecognisedError = CountryNotRecognisedError

    objects = OrderManager.from_queryset(OrderQueryset)()

    class Meta:
        """Meta class for the Order model."""

        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order: {self.order_ID}"

    def is_dispatched(self):
        """Return True if the order is dispatched, otherwise return False."""
        return self.dispatched_at is not None

    def total_weight(self):
        """Return the combined weight of the order."""
        return sum((sale.total_weight() for sale in self.productsale_set.all()))

    def vat_paid(self):
        """Return the VAT paid on the order."""
        if self.country.vat_is_required() == self.country.VAT_NEVER:
            return 0
        else:
            return sum((sale._vat_paid() for sale in self.productsale_set.all()))

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
                self.vat_paid(),
                self.channel_fee_paid(),
                self.purchase_price(),
                self.postage_price,
            )
        )
        return self.total_paid_GBP - expenses

    def profit_percentage(self):
        """Return the percentage of the amount paid for the order that is profit."""
        return int((self.profit() / self.total_paid_GBP) * 100)

    def _get_postage_price(self):
        shipping_service = self.shipping_rule.shipping_service
        price = ShippingPrice.objects.find_shipping_price(
            country=self.country, shipping_service=shipping_service
        )
        return price.price(self.total_weight())

    def _set_postage_price(self):
        try:
            self.postage_price = self._get_postage_price()
        except Exception:
            self.postage_price = None
            self.postage_price_success = False
        else:
            self.postage_price_success = True
        if self.total_paid == 0 or self.total_paid_GBP == 0:
            self.postage_price_success = False
        self.save()

    def up_to_date_details(self):
        """Return True if all data requests have been attempted, otherwise False."""
        if self.postage_price_success is None:
            return False
        if any((sale.details_success is None for sale in self.productsale_set.all())):
            return False
        return True

    def profit_calculable(self):
        """Return True if all data requests have been retrieved, otherwise False."""
        if self.postage_price_success is not True:
            return False
        if any(
            (sale.details_success is not True for sale in self.productsale_set.all())
        ):
            return False
        return True

    def packed_by(self):
        """Return the packer who packed this order."""
        try:
            return self.packingrecord.packed_by
        except Exception:
            return None
