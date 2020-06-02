"""The Order model."""
from datetime import datetime, timedelta

from ccapi import CCAPI
from django.db import models
from django.utils import timezone

from shipping.models import Country, CourierService, ShippingRule

from .channel import Channel
from .product_sale import ProductSale


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


class OrderManager(models.Manager):
    """Model manager for orders.Order."""

    def update_orders(self, number_of_days=None):
        """Update orders from Cloud Commerce."""
        orders_to_dispatch = self._get_orders_for_dispatch()
        dispatched_orders = self._get_dispatched_orders(number_of_days=number_of_days)
        orders = orders_to_dispatch + dispatched_orders
        for order in orders:
            order_obj = self._create_or_update_from_cc_order(order)
            if order_obj is not None:
                self._update_sales(order_obj, order)
        self._update_cancelled_orders(orders_to_dispatch)

    def _update_sales(self, order_obj, order):
        """Add product sales to the ProductSale model."""
        for product in order.products:
            price = int(product.price * 100)
            sale, _ = ProductSale._default_manager.get_or_create(
                order=order_obj,
                product_ID=product.product_id,
                defaults={"quantity": product.quantity, "price": price},
            )
            if sale.quantity != product.quantity or sale.price != price:
                sale.quantity = product.quantity
                sale.price = price
                sale.save()

    def _update_cancelled_orders(self, orders_to_dispatch):
        """Mark cancelled orders."""
        undispatched_order_IDs = [order.order_id for order in orders_to_dispatch]
        unaccounted_orders = self.filter(
            cancelled=False, dispatched_at__isnull=True, ignored=False
        ).exclude(order_ID__in=undispatched_order_IDs)
        for order in unaccounted_orders:
            order.check_cancelled()

    def _get_orders_for_dispatch(self):
        """Return undispatched Cloud Commerce orders."""
        return CCAPI.get_orders_for_dispatch(order_type=0, number_of_days=0)

    def _get_dispatched_orders(self, number_of_days=None):
        """Return dispatched Cloud Commerce orders."""
        if number_of_days is None:
            number_of_days = 1
        return CCAPI.get_orders_for_dispatch(
            order_type=1, number_of_days=number_of_days
        )

    def _create_or_update_from_cc_order(self, order):
        """Create or update an order from Cloud Commerce."""
        try:
            existing_order = self.get(order_ID=order.order_id)
        except Order.DoesNotExist:
            existing_order = None
        if existing_order is not None and existing_order.dispatched_at is not None:
            # The order exists and already shows as dispatched
            return None
        order_details = self._cc_order_details(order)
        if existing_order is None:
            # The order does not exist and will be created
            new_order = Order(**order_details)
            new_order.save()
            return new_order
        else:
            # The order does exist but has not been dispatched
            self.filter(order_ID=order.order_id).update(**order_details)
            existing_order.refresh_from_db()
            return existing_order

    def _parse_dispatch_date(self, dispatch_date):
        """Return dispatch date as tz aware if it is not the EPOCH, otherwise return None."""
        if dispatch_date != Order.DISPATCH_EPOCH:
            return timezone.make_aware(dispatch_date)
        else:
            return None

    def _cc_order_details(self, order):
        """Return a dict of Order kwargs from a Cloud Commerce order."""
        channel, _ = Channel._default_manager.get_or_create(name=order.channel_name)
        try:
            country = Country._default_manager.get(
                country_ID=order.delivery_country_code
            )
        except Country.DoesNotExist:
            raise CountryNotRecognisedError(order.country_code, order.order_id)
        shipping_rule = self._get_shipping_rule(order)
        if shipping_rule is not None:
            courier_service = shipping_rule.courier_service
        else:
            courier_service = None
        dispatched_at = self._parse_dispatch_date(order.dispatch_date)
        kwargs = {
            "order_ID": order.order_id,
            "customer_ID": order.customer_id,
            "recieved_at": timezone.make_aware(order.date_recieved),
            "dispatched_at": dispatched_at,
            "cancelled": order.cancelled,
            "channel": channel,
            "channel_order_ID": order.external_transaction_id,
            "country": country,
            "shipping_rule": shipping_rule,
            "courier_service": courier_service,
            "tracking_number": order.tracking_code or None,
            "ignored": not order.can_process_order,
        }
        return kwargs

    def _get_shipping_rule(self, order):
        """Return the shipping rule used on the order if possible."""
        rule_name = order.default_cs_rule_name.split(" - ")[0]
        try:
            return ShippingRule.objects.get(name=rule_name)
        except ShippingRule.DoesNotExist:
            return None


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

    def check_cancelled(self):
        """Check if the order has been cancelled and update the cancelled attribute."""
        if self.cancelled is True or self.customer_ID is None:
            return
        recent_orders = CCAPI.recent_orders_for_customer(customer_ID=self.customer_ID)
        if self.order_ID in recent_orders:
            order = recent_orders[self.order_ID]
            if order.status == order.CANCELLED:
                self.cancelled = True
                self.save()
            elif order.status == order.IGNORED:
                self.ignored = True
                self.save()
