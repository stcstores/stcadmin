"""Models for the Wowcher app."""

import datetime

import pywowcher
from ccapi import CCAPI, NewOrderItem
from django.db import models
from django.utils import timezone


class ActiveDealManager(models.Manager):
    """Manager for currently active Wowcher deals."""

    def get_queryset(self):
        """Return a queryset of WowcherDeals that are currently active."""
        return super().get_queryset().filter(ended__isnull=True, inactive=False)


class WowcherDeal(models.Model):
    """Model for Wowcher deals."""

    deal_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    product_SKU = models.CharField(max_length=255)
    product_ID = models.CharField(max_length=255)
    item_net = models.DecimalField(max_digits=6, decimal_places=2)
    item_gross = models.DecimalField(max_digits=6, decimal_places=2)
    total_net = models.DecimalField(max_digits=6, decimal_places=2)
    total_gross = models.DecimalField(max_digits=6, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField(blank=True, null=True, default=None)
    inactive = models.BooleanField(default=False)

    objects = models.Manager()
    active = ActiveDealManager()

    class Meta:
        """Meta class for the WowcherDeal model."""

        verbose_name = "Wowcher Deal"
        verbose_name_plural = "Wowcher Deals"
        ordering = ("created",)

    def __str__(self):
        return f"Wowcher Deal {self.deal_id} - {self.name}"

    def end_deal(self):
        """Mark the Wowcher deal as ended."""
        self.ended = timezone.now()
        self.inactive = True
        self.save()


class OrderToDispatchManager(models.Manager):
    """ModelManager for Wowcher orders awaiting dispatch."""

    def get_queryset(self):
        """Return a queryset of WowcherOrders awaiting dispatch."""
        return (
            super()
            .get_queryset()
            .filter(
                canceled=False,
                status__in=[
                    WowcherOrder.STATUS_RECEIVED_BY_MERCHANT,
                    WowcherOrder.STATUS_READY_FOR_DESPATCH,
                ],
            )
        )


class WowcherOrder(models.Model):
    """Model for Wowcher orders."""

    STATUS_RECEIVED_BY_MERCHANT = "status_received_by_merchant"
    STATUS_READY_FOR_DESPATCH = "status_ready_for_despatch"
    STATUS_DESPATCHED = "status_despatched"
    STATUS_CHOICED = (
        (STATUS_RECEIVED_BY_MERCHANT, "Recieved by merchant"),
        (STATUS_READY_FOR_DESPATCH, "Ready for dispatch"),
        (STATUS_DESPATCHED, "Dispatched"),
    )

    deal = models.ForeignKey(WowcherDeal, on_delete=models.CASCADE)
    wowcher_code = models.CharField(max_length=255)
    cloud_commerce_order_ID = models.CharField(
        max_length=255, blank=True, null=True, default=None
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICED)
    canceled = models.BooleanField(default=False)

    objects = models.Manager()
    to_dispatch = OrderToDispatchManager()

    class Meta:
        """Meta class for the WowcherOrder model."""

        verbose_name = "Wowcher Order"
        verbose_name_plural = "Wowcher Orders"

    def __str__(self):
        return f"Wowcher Order {self.wowcher_code}"


def update_wowcher_orders():
    """Get new orders for all current Wowcher deals."""
    deals = WowcherDeal.active.all()
    for deal in deals:
        update_wowcher_deal(deal)


def update_wowcher_deal(deal):
    """Get new orders for a Wowcher deal."""
    orders = pywowcher.get_orders(deal_id=deal.deal_id)
    existing_order_codes = [order.wowcher_code for order in deal.wowcherorder_set.all()]
    new_orders = [
        order for order in orders if order.wowcher_code not in existing_order_codes
    ]
    new_orders = new_orders[:1]  # Limit for testing
    for order in new_orders:
        ProcesssWowcherOrder(deal, order)


def dispatch_wowcher_orders():
    """Mark dispatched Wowcher orders as such."""
    dispatched_orders = {
        order.order_id: order
        for order in CCAPI.get_orders_for_dispatch(include_products=0, number_of_days=2)
    }
    undispatched_wowcher_orders = WowcherOrder.to_dispatch.all()
    for order in undispatched_wowcher_orders:
        if order.cloud_commerce_order_ID in dispatched_orders:
            kwargs = {
                pywowcher.REFERENCE: WowcherOrder.wowcher_code,
                pywowcher.STATUS: pywowcher.DISPATCHED,
            }
            cc_order = dispatched_orders[order.cloud_commerce_order_ID]
            if cc_order.tracking_code:
                kwargs[pywowcher.TRACKING_NUMBER] = cc_order.tracking_code
            pywowcher.set_order_status(**kwargs)
            order.status = WowcherOrder.STATUS_DESPATCHED
            order.save()


class ProcesssWowcherOrder:
    """Add a new Wowcher order to the database and to Cloud Commerce."""

    BILLING = "Billing"
    DELIVERY = "Delivery"
    ADMIN = "Admin"
    SELLING_CHANNEL_ID = "3541"

    def __init__(self, deal, wowcher_order):
        """Add a new Wowcher order to the database and to Cloud Commerce."""
        self.wowcher_order = wowcher_order
        self.deal = deal
        self.create_wowcher_order()
        self.create_order_in_cloud_commerce()
        self.db_wowhcer_order.cloud_commerce_order_ID = (
            self.cloud_commerce_order.order_id
        )
        self.db_wowhcer_order.save()

    def create_wowcher_order(self):
        """Create the order in the database."""
        self.db_wowhcer_order = WowcherOrder(
            deal=self.deal,
            wowcher_code=self.wowcher_order.wowcher_code,
            status=WowcherOrder.STATUS_RECEIVED_BY_MERCHANT,
        )
        self.db_wowhcer_order.save()

    def create_order_in_cloud_commerce(self):
        """Add the order to Cloud Commerce."""
        self.customer_ID = self.add_customer()
        self.billing_address_ID = self.add_address(self.BILLING)
        self.delivery_address_ID = self.add_address(self.DELIVERY)
        self.order_items = self.get_order_items()
        self.cloud_commerce_order = self.create_order()
        self.create_payment()

    def customer_name(self):
        """Return a parsed customer name."""
        o = self.wowcher_order
        return f"{o.delivery_title} {o.delivery_first_name} {o.delivery_last_name}"

    def add_customer(self):
        """Add a new customer to Cloud Commerce based on the Wowcher order details."""
        return CCAPI.add_customer(
            customer_name=self.customer_name(),
            address_1=self.wowcher_order.delivery_line_1,
            address_2=self.wowcher_order.delivery_line_2,
            town=self.wowcher_order.delivery_city,
            country=self.wowcher_order.delivery_country,
            post_code=self.wowcher_order.delivery_postcode,
            selling_channel_id=self.SELLING_CHANNEL_ID,
        )

    def add_address(self, address_type):
        """Add a customer address to Cloud Commerce based on the Wowcher order details."""
        return CCAPI.add_address(
            self.customer_ID,
            address_type=address_type,
            address_1=self.wowcher_order.delivery_line_1,
            address_2=self.wowcher_order.delivery_line_2,
            town=self.wowcher_order.delivery_city,
            country=self.wowcher_order.delivery_country,
            post_code=self.wowcher_order.delivery_postcode,
        )

    def get_order_items(self):
        """Return a ccapi.NewOrderItem for the Wowcher order."""
        order = NewOrderItem(
            product_id=self.deal.product_ID,
            item_net=self.deal.total_net,
            item_gross=self.deal.item_gross,
            total_net=self.deal.total_net,
            total_gross=self.deal.total_gross,
            item_discount_net=0,
            quantity=1,
        )
        return [order]

    def create_order(self):
        """Create the order in Cloud Commerce."""
        return CCAPI.create_order(
            items=self.order_items,
            customer_id=str(self.customer_ID),
            delivery_address_id=str(self.delivery_address_ID),
            billing_address_id=str(self.billing_address_ID),
            delivery_date=datetime.datetime.now() + datetime.timedelta(days=5),
            carriage_net=1.79,
            carriage_vat=0.36,
            total_net=12.50,
            total_vat=2.86,
            total_gross=17.15,
            discount_net=0.0,
        )

    def create_payment(self):
        """Mark the Cloud Commerce order as paid."""
        CCAPI.create_payment(
            customer_id=self.customer_ID,
            invoice_id=self.cloud_commerce_order.invoice_id,
            amount=self.cloud_commerce_order.total_gross,
        )
