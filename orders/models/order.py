"""The Order model."""
from datetime import datetime

import pytz
from ccapi import CCAPI
from django.db import models
from django.utils.timezone import make_aware

from shipping.models import Country, Service, ShippingRule

from .channel import Channel
from .product_sale import ProductSale


class Order(models.Model):
    """Model for Cloud Commerce Orders."""

    TIME_ZONE = "Europe/London"
    DISPATCH_EPOCH = datetime(2000, 1, 1, 0, 0)

    order_ID = models.CharField(max_length=12, unique=True, db_index=True)
    customer_ID = models.CharField(max_length=12, blank=True, null=True)
    recieved_at = models.DateTimeField()
    dispatched_at = models.DateTimeField(blank=True, null=True)
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

    def __str__(self):
        return f"Order: {self.order_ID}"

    def is_dispatched(self):
        """Return True if the order is dispatched, otherwise return False."""
        return self.dispatched_at is not None

    @classmethod
    def make_tz_aware(cls, d):
        """Make a naive datetime timezone aware."""
        return make_aware(d, timezone=pytz.timezone(cls.TIME_ZONE))

    @classmethod
    def update(cls, number_of_days=None):
        """Update orders from Cloud Commerce."""
        orders_to_dispatch = cls.get_orders_for_dispatch()
        dispatched_orders = cls.get_dispatched_orders()
        orders = orders_to_dispatch + dispatched_orders
        for order in orders:
            order_obj = cls.create_or_update_order(order)
            if order_obj is not None:
                cls.update_sales(order_obj, order)

    @classmethod
    def update_sales(cls, order_obj, order):
        """Add product sales to the ProductSale model."""
        for product in order.products:
            price = int(product.price * 100)
            sale, _ = ProductSale._default_manager.get_or_create(
                order=order_obj,
                product_ID=product.id,
                defaults={"quantity": product.quantity, "price": price},
            )
            if sale.quantity != product.quantity or sale.price != price:
                sale.quantity = product.quantity
                sale.price = price
                sale.save()

    @classmethod
    def get_orders_for_dispatch(cls):
        """Return undispatched Cloud Commerce orders."""
        return CCAPI.get_orders_for_dispatch(order_type=0, number_of_days=0)

    @classmethod
    def get_dispatched_orders(cls, number_of_days=None):
        """Return dispatched Cloud Commerce orders."""
        if number_of_days is None:
            number_of_days = 1
        return CCAPI.get_orders_for_dispatch(
            order_type=1, number_of_days=number_of_days
        )

    @classmethod
    def create_or_update_order(cls, order):
        """Create or update an order from Cloud Commerce."""
        try:
            existing_order = cls._default_manager.get(order_ID=order.order_id)
        except cls.DoesNotExist:
            existing_order = None
        if existing_order is not None and existing_order.dispatched_at is not None:
            # The order exists and already shows as dispatched
            return None
        order_details = cls.order_details(order)
        if existing_order is None:
            # The order does not exist and will be created
            new_order = cls._default_manager.create(**order_details)
            return new_order
        else:
            # The order does exist but has not been dispatched
            cls._default_manager.filter(order_ID=order.order_id).update(**order_details)
            existing_order.refresh_from_db()
            return existing_order

    @classmethod
    def parse_dispatch_date(cls, dispatch_date):
        """Return dispatch date as tz aware if it is not the EPOCH, otherwise return None."""
        if dispatch_date != cls.DISPATCH_EPOCH:
            return cls.make_tz_aware(dispatch_date)
        else:
            return None

    @classmethod
    def order_details(cls, order):
        """Return a dict of order details."""
        channel, _ = Channel._default_manager.get_or_create(name=order.channel_name)
        country = Country._default_manager.get(country_ID=order.delivery_country_code)
        shipping_rule = cls.get_shipping_rule(order)
        shipping_service = shipping_rule.service
        dispatched_at = cls.parse_dispatch_date(order.dispatch_date)
        kwargs = {
            "order_ID": order.order_id,
            "customer_ID": order.customer_id,
            "recieved_at": cls.make_tz_aware(order.date_recieved),
            "dispatched_at": dispatched_at,
            "cancelled": order.cancelled,
            "channel": channel,
            "channel_order_ID": order.external_transaction_id,
            "country": country,
            "shipping_rule": shipping_rule,
            "shipping_service": shipping_service,
        }
        return kwargs

    @classmethod
    def get_shipping_rule(cls, order):
        """Return the shipping rule used on the order if possible."""
        rule_name = order.default_cs_rule_name.split(" - ")[0]
        try:
            return ShippingRule._default_manager.get(name=rule_name)
        except ShippingRule.DoesNotExist:
            return None
