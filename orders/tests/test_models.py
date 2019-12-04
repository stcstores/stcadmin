from datetime import datetime

import pytz
from django.utils.timezone import make_aware

from orders import models
from print_audit.models import CloudCommerceUser
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestChannel(STCAdminTest):
    def test_create_object(self):
        name = "Test Channel"
        channel = models.Channel.objects.create(name=name)
        self.assertEqual(name, channel.name)


class TestOrder(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "shipping/services",
        "shipping/shipping_rules",
    )

    def aware_tz(self, date):
        return make_aware(date, timezone=pytz.timezone("Europe/London"))

    def test_create_object(self):
        order_ID = "3849383"
        customer_ID = "9465165"
        recieved = datetime(year=2019, month=11, day=4, hour=13, minute=52)
        dispatched = datetime(year=2019, month=11, day=4, hour=14, minute=12)
        channel = models.Channel.objects.create(name="Test Channel")
        channel_order_ID = "4883-AFD-38349"
        country = models.Country.objects.get(id=1)
        shipping_rule = models.ShippingRule.objects.get(id=1)
        service = models.Service.objects.get(id=1)
        order = models.Order.objects.create(
            order_ID=order_ID,
            customer_ID=customer_ID,
            recieved=recieved,
            dispatched=dispatched,
            channel=channel,
            channel_order_ID=channel_order_ID,
            country=country,
            shipping_rule=shipping_rule,
            shipping_service=service,
        )
        self.assertEqual(order_ID, order.order_ID)
        self.assertEqual(customer_ID, order.customer_ID)
        self.assertEqual(self.aware_tz(recieved), order.recieved)
        self.assertEqual(self.aware_tz(dispatched), order.dispatched)
        self.assertEqual(channel, order.channel)
        self.assertEqual(channel_order_ID, order.channel_order_ID)
        self.assertEqual(country, order.country)
        self.assertEqual(shipping_rule, order.shipping_rule)
        self.assertEqual(service, order.shipping_service)

    def test_save_tz_aware_date(self):
        naive_date = datetime(year=2019, month=11, day=4, hour=13, minute=52)
        aware_date = make_aware(naive_date, timezone=pytz.timezone("Europe/London"))
        order = models.Order.objects.create(
            order_ID="3849383", recieved=aware_date, dispatched=aware_date
        )
        self.assertEqual(aware_date, order.recieved)
        self.assertEqual(aware_date, order.dispatched)


class TestProductSale(STCAdminTest):
    def test_create_object(self):
        date = datetime(year=2019, month=11, day=4, hour=13, minute=52)
        order = models.Order.objects.create(order_ID="3849383", recieved=date)
        product_ID = "3940393"
        quantity = 5
        price = 2599
        sale = models.ProductSale.objects.create(
            order=order, product_ID=product_ID, quantity=quantity, price=price
        )
        self.assertEqual(order, sale.order)
        self.assertEqual(product_ID, sale.product_ID)
        self.assertEqual(quantity, sale.quantity)
        self.assertEqual(price, sale.price)


class TestPackingRecord(STCAdminTest):
    def test_create_object(self):
        self.create_user()
        date = datetime(year=2019, month=11, day=4, hour=13, minute=52)
        order = models.Order.objects.create(order_ID="3849383", recieved=date)
        user = CloudCommerceUser.objects.create(
            user_id="393",
            stcadmin_user=self.user,
            first_name="Test",
            second_name="User",
        )
        packing_record = models.PackingRecord.objects.create(
            order=order, packed_by=user
        )
        self.assertEqual(order, packing_record.order)
        self.assertEqual(user, packing_record.packed_by)
