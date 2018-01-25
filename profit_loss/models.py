import pytz
from django.db import models
from django.utils.timezone import is_naive
from order_profit import OrderProfit

from spring_manifest.models import CloudCommerceCountryID


class Order(models.Model):

    class Meta:
        ordering = ['-dispatch_date']

    order_id = models.PositiveIntegerField(unique=True)
    customer_id = models.PositiveIntegerField()
    country = models.ForeignKey(
        CloudCommerceCountryID, on_delete=models.SET_NULL, null=True,
        blank=True)
    department = models.CharField(max_length=255, default='None')
    weight = models.PositiveIntegerField()
    vat_rate = models.PositiveIntegerField(null=True, blank=True)
    price = models.PositiveIntegerField()
    purchase_price = models.PositiveIntegerField()
    postage_price = models.PositiveIntegerField()
    item_count = models.PositiveIntegerField()
    date_recieved = models.DateTimeField()
    dispatch_date = models.DateTimeField()
    shipping_service = models.CharField(max_length=250)

    def vat(self):
        if self.vat_rate is not None:
            return int(
                ((self.price / (1 + (self.vat_rate / 100))) - self.price) * -1)

    def profit(self):
        if self.vat() is not None:
            return self.price - sum([
                self.postage_price, self.purchase_price, self.channel_fee(),
                self.vat()])

    def profit_percentage(self):
        profit = self.profit()
        if profit is not None:
            return int((self.profit() / self.price) * 100)

    def profit_no_vat(self):
        return self.price - sum([
            self.postage_price, self.purchase_price, self.channel_fee()])

    def channel_fee(self):
        return int(float(self.price / 100) * 15)

    def save(self, *args, **kwargs):
        self.date_recieved = self.localise_datetime(self.date_recieved)
        self.dispatch_date = self.localise_datetime(self.dispatch_date)
        super().save(*args, **kwargs)

    @staticmethod
    def localise_datetime(date_input):
        if date_input is not None and is_naive(date_input):
            tz = pytz.timezone('Europe/London')
            date_input = date_input.replace(tzinfo=tz)
        return date_input

    def __str__(self):
        return str(self.order_id)


class UpdateOrderProfit(OrderProfit):

    number_of_days = 4

    def __init__(self):
        super().__init__()
        new_orders = [
            Order(
                order_id=o.order_id, customer_id=o.customer_id,
                department=o.department, weight=o.weight, vat_rate=o.vat_rate,
                country=CloudCommerceCountryID._base_manager.get(
                    cc_id=o.country.id),
                price=o.price, purchase_price=o.purchase_price,
                postage_price=o.postage_price, item_count=o.item_count,
                date_recieved=Order.localise_datetime(o.date_recieved),
                dispatch_date=Order.localise_datetime(o.dispatch_date),
                shipping_service=o.courier)
            for o in self.orders]
        Order._base_manager.bulk_create(new_orders)

    def filter_orders(self, orders):
        orders = super().filter_orders(orders)
        existing_order_ids = Order._base_manager.all().values_list(
            'order_id', flat=True)
        orders = [o for o in orders if o.order_id not in existing_order_ids]
        return orders
