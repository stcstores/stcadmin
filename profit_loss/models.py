"""Models for proift loss."""

import pytz
from django.db import models, transaction
from django.utils.timezone import is_naive
from order_profit import OrderProfit
from spring_manifest.models import CloudCommerceCountryID


class Order(models.Model):
    """Model for Cloud Commerce orders."""

    order_id = models.PositiveIntegerField(unique=True)
    customer_id = models.PositiveIntegerField()
    country = models.ForeignKey(
        CloudCommerceCountryID, on_delete=models.SET_NULL, null=True, blank=True
    )
    department = models.CharField(max_length=255, default="None")
    weight = models.PositiveIntegerField()
    vat_rate = models.PositiveIntegerField(null=True, blank=True)
    price = models.PositiveIntegerField()
    purchase_price = models.PositiveIntegerField()
    postage_price = models.PositiveIntegerField()
    item_count = models.PositiveIntegerField()
    date_recieved = models.DateTimeField()
    dispatch_date = models.DateTimeField()
    shipping_service = models.CharField(max_length=250)

    class Meta:
        """Meta class for Order."""

        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-dispatch_date"]

    def vat(self):
        """Return VAT paid on order."""
        if self.vat_rate is not None:
            return int(((self.price / (1 + (self.vat_rate / 100))) - self.price) * -1)

    def profit(self):
        """Return profit made on order."""
        if self.vat() is not None:
            return self.price - sum(
                [
                    self.postage_price,
                    self.purchase_price,
                    self.channel_fee(),
                    self.vat(),
                ]
            )

    def profit_percentage(self):
        """Return percentage of price paid that is profit."""
        profit = self.profit()
        if profit is not None:
            return int((self.profit() / self.price) * 100)

    def profit_no_vat(self):
        """Return profit on order not taking VAT into account."""
        return self.price - sum(
            [self.postage_price, self.purchase_price, self.channel_fee()]
        )

    def channel_fee(self):
        """Return amount paid as the channel fee."""
        return int(float(self.price / 100) * 15)

    def save(self, *args, **kwargs):
        """Set time zone for date recieved and dispatch date."""
        self.date_recieved = self.localise_datetime(self.date_recieved)
        self.dispatch_date = self.localise_datetime(self.dispatch_date)
        super().save(*args, **kwargs)

    @staticmethod
    def localise_datetime(date_input):
        """Return date_input as localised datetime."""
        if date_input is not None and is_naive(date_input):
            tz = pytz.timezone("Europe/London")
            date_input = date_input.replace(tzinfo=tz)
        return date_input

    def __str__(self):
        return str(self.order_id)


class Product(models.Model):
    """Model for Cloud Commerce Products."""

    sku = models.CharField(max_length=20)
    range_id = models.IntegerField()
    product_id = models.IntegerField()
    name = models.TextField()
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, models.CASCADE)

    class Meta:
        """Meta class for Product."""

        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __repr__(self):
        return "{} - {} x {}".format(self.sku, self.name, self.quantity)


class UpdateOrderProfit(OrderProfit):
    """Add profit_loss orders to database."""

    number_of_days = 4

    @transaction.atomic
    def __init__(self):
        """Add profit_loss orders to database."""
        super().__init__()
        for o in self.orders:
            order = Order(
                order_id=o.order_id,
                customer_id=o.customer_id,
                department=o.department,
                weight=o.weight,
                vat_rate=o.vat_rate,
                country=CloudCommerceCountryID._base_manager.get(cc_id=o.country.id),
                price=o.price,
                purchase_price=o.purchase_price,
                postage_price=o.postage_price,
                item_count=o.item_count,
                date_recieved=Order.localise_datetime(o.date_recieved),
                dispatch_date=Order.localise_datetime(o.dispatch_date),
                shipping_service=o.courier,
            )
            order.save()
            for p in o.products:
                product = Product(
                    sku=p.sku,
                    range_id=p.range_id,
                    product_id=p.product_id,
                    name=p.name,
                    quantity=p.quantity,
                    order=order,
                )
                product.save()

    def filter_orders(self, orders):
        """Filter out orders that already exist in the database."""
        orders = super().filter_orders(orders)
        existing_order_ids = Order._base_manager.all().values_list(
            "order_id", flat=True
        )
        orders = [o for o in orders if o.order_id not in existing_order_ids]
        return orders
