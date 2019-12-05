from datetime import datetime
from unittest.mock import Mock, call, patch

import pytz
from django.utils.timezone import make_aware

from orders import models
from print_audit.models import CloudCommerceUser
from shipping import models as shipping_models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestChannel(STCAdminTest):
    fixtures = ("orders/channels",)

    def test_create_object(self):
        name = "Test Channel"
        channel = models.Channel.objects.create(name=name)
        self.assertEqual(name, channel.name)

    def test_str(self):
        channel = models.Channel.objects.get(id=1)
        self.assertEqual(channel.name, str(channel))


class TestOrder(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "shipping/services",
        "shipping/shipping_rules",
        "orders/channels",
        "orders/orders",
    )

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("orders.models.order.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

        self.order_ID = "3849389383"
        self.customer_ID = "59403"
        self.recieved = datetime(2019, 11, 3, 12, 23)
        self.dispatched = datetime(2019, 11, 3, 13, 57)
        self.aware_recieved = self.aware_tz(self.recieved)
        self.aware_dispatched = self.aware_tz(self.dispatched)
        self.cancelled = False
        self.channel = models.Channel.objects.create(name="Test Channel")
        self.channel_order_ID = "8504389BHF9393"
        self.country = shipping_models.Country.objects.get(id=1)
        self.shipping_rule = shipping_models.ShippingRule.objects.get(id=1)
        self.service = self.shipping_rule.service
        self.shipping_rule_name = " - ".join(
            (self.shipping_rule.name, self.shipping_rule.service.name)
        )

        self.product_ID = "2949030"
        self.product_price = 4.50
        self.product_quantity = 3

    def create_mock_order(
        self,
        order_id=None,
        customer_id=None,
        date_recieved=None,
        dispatch_date=None,
        cancelled=None,
        channel_name=None,
        external_transaction_id=None,
        delivery_country_code=None,
        default_cs_rule_name=None,
        products=None,
    ):
        if order_id is None:
            order_id = self.order_ID
        if customer_id is None:
            customer_id = self.customer_ID
        if date_recieved is None:
            date_recieved = self.recieved
        if dispatch_date is None:
            dispatch_date = self.dispatched
        if cancelled is None:
            cancelled = self.cancelled
        if channel_name is None:
            channel_name = self.channel.name
        if external_transaction_id is None:
            external_transaction_id = self.channel_order_ID
        if delivery_country_code is None:
            delivery_country_code = self.country.country_ID
        if default_cs_rule_name is None:
            default_cs_rule_name = self.shipping_rule_name
        if products is None:
            products = [self.create_mock_product()]
        return Mock(
            order_id=order_id,
            customer_id=customer_id,
            date_recieved=date_recieved,
            dispatch_date=dispatch_date,
            cancelled=cancelled,
            channel_name=channel_name,
            external_transaction_id=external_transaction_id,
            delivery_country_code=delivery_country_code,
            default_cs_rule_name=default_cs_rule_name,
            products=products,
        )

    def create_mock_product(self, product_ID=None, price=None, quantity=None):
        if product_ID is None:
            product_ID = self.product_ID
        if price is None:
            price = self.product_price
        if quantity is None:
            quantity = self.product_quantity
        return Mock(id=product_ID, price=price, quantity=quantity)

    def aware_tz(self, date):
        return make_aware(date, timezone=pytz.timezone("Europe/London"))

    def test_create_object(self):
        order = models.Order.objects.create(
            order_ID=self.order_ID,
            customer_ID=self.customer_ID,
            recieved=self.aware_recieved,
            dispatched=self.aware_dispatched,
            channel=self.channel,
            channel_order_ID=self.channel_order_ID,
            country=self.country,
            shipping_rule=self.shipping_rule,
            shipping_service=self.service,
        )
        self.assertEqual(self.order_ID, order.order_ID)
        self.assertEqual(self.customer_ID, order.customer_ID)
        self.assertEqual(self.aware_recieved, order.recieved)
        self.assertEqual(self.aware_dispatched, order.dispatched)
        self.assertEqual(self.channel, order.channel)
        self.assertEqual(self.channel_order_ID, order.channel_order_ID)
        self.assertEqual(self.country, order.country)
        self.assertEqual(self.shipping_rule, order.shipping_rule)
        self.assertEqual(self.service, order.shipping_service)
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_str(self):
        order = models.Order.objects.get(id=1)
        self.assertEqual(f"Order: {order.order_ID}", str(order))

    def test_order_details(self):
        order = self.create_mock_order()
        order_details = models.Order.order_details(order)
        self.assertIsInstance(order_details, dict)
        self.assertIn("order_ID", order_details)
        self.assertEqual(self.order_ID, order_details["order_ID"])
        self.assertIn("customer_ID", order_details)
        self.assertEqual(self.customer_ID, order_details["customer_ID"])
        self.assertIn("recieved", order_details)
        self.assertEqual(self.aware_tz(self.recieved), order_details["recieved"])
        self.assertIn("dispatched", order_details)
        self.assertEqual(self.aware_tz(self.dispatched), order_details["dispatched"])
        self.assertIn("cancelled", order_details)
        self.assertEqual(self.cancelled, order_details["cancelled"])
        self.assertIn("channel", order_details)
        self.assertEqual(self.channel, order_details["channel"])
        self.assertIn("channel_order_ID", order_details)
        self.assertEqual(self.channel_order_ID, order_details["channel_order_ID"])
        self.assertIn("country", order_details)
        self.assertEqual(self.country, order_details["country"])
        self.assertIn("shipping_rule", order_details)
        self.assertEqual(self.shipping_rule, order_details["shipping_rule"])
        self.assertIn("shipping_service", order_details)
        self.assertEqual(self.service, order_details["shipping_service"])
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_parse_dispatch_date(self):
        self.assertEqual(
            self.aware_dispatched, models.Order.parse_dispatch_date(self.dispatched)
        )
        self.assertIsNone(models.Order.parse_dispatch_date(models.Order.DISPATCH_EPOCH))
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_get_shipping_rule(self):
        order = Mock(default_cs_rule_name=self.shipping_rule_name)
        self.assertEqual(self.shipping_rule, models.Order.get_shipping_rule(order))
        order = Mock(default_cs_rule_name="Non Existant Rule - Non Existant Service")
        self.assertIsNone(models.Order.get_shipping_rule(order))
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_create_new_order(self):
        self.assertFalse(models.Order.objects.filter(order_ID=self.order_ID).exists())
        mock_order = self.create_mock_order()
        order = models.Order.create_or_update_order(mock_order)
        self.assertTrue(models.Order.objects.filter(order_ID=self.order_ID).exists())
        self.assertEqual(self.order_ID, order.order_ID)
        self.assertEqual(self.customer_ID, order.customer_ID)
        self.assertEqual(self.aware_recieved, order.recieved)
        self.assertEqual(self.aware_dispatched, order.dispatched)
        self.assertEqual(self.channel, order.channel)
        self.assertEqual(self.channel_order_ID, order.channel_order_ID)
        self.assertEqual(self.country, order.country)
        self.assertEqual(self.shipping_rule, order.shipping_rule)
        self.assertEqual(self.service, order.shipping_service)
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_update_order(self):
        self.assertFalse(models.Order.objects.filter(order_ID=self.order_ID).exists())
        models.Order.objects.create(
            order_ID=self.order_ID, recieved=self.aware_tz(datetime(2019, 4, 3, 7, 23))
        )
        mock_order = self.create_mock_order()
        order = models.Order.create_or_update_order(mock_order)
        self.assertEqual(self.order_ID, order.order_ID)
        self.assertEqual(self.customer_ID, order.customer_ID)
        self.assertEqual(self.aware_recieved, order.recieved)
        self.assertEqual(self.aware_dispatched, order.dispatched)
        self.assertEqual(self.channel, order.channel)
        self.assertEqual(self.channel_order_ID, order.channel_order_ID)
        self.assertEqual(self.country, order.country)
        self.assertEqual(self.shipping_rule, order.shipping_rule)
        self.assertEqual(self.service, order.shipping_service)
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_dispatched_order_does_not_update(self):
        self.assertFalse(models.Order.objects.filter(order_ID=self.order_ID).exists())
        recieved = self.aware_tz(datetime(2019, 4, 3, 7, 23))
        dispatched = self.aware_tz(datetime(2019, 4, 3, 12, 47))
        models.Order.objects.create(
            order_ID=self.order_ID, recieved=recieved, dispatched=dispatched
        )
        mock_order = self.create_mock_order()
        returned_value = models.Order.create_or_update_order(mock_order)
        self.assertIsNone(returned_value)
        order = models.Order.objects.get(order_ID=self.order_ID)
        self.assertEqual(self.order_ID, order.order_ID)
        self.assertIsNone(order.customer_ID)
        self.assertEqual(recieved, order.recieved)
        self.assertEqual(dispatched, order.dispatched)
        self.assertIsNone(order.channel)
        self.assertIsNone(order.channel_order_ID)
        self.assertIsNone(order.country)
        self.assertIsNone(order.shipping_rule)
        self.assertIsNone(order.shipping_service)
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_get_orders_for_dispatch(self):
        mock_orders = [
            self.create_mock_order(order_id=_) for _ in ("294039830", "856939380")
        ]
        self.mock_CCAPI.get_orders_for_dispatch.return_value = mock_orders
        returned_value = models.Order.get_orders_for_dispatch()
        self.assertEqual(mock_orders, returned_value)
        self.mock_CCAPI.get_orders_for_dispatch.assert_called_once_with(
            order_type=0, number_of_days=0
        )
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 1)

    def test_get_dispatched_orders(self):
        mock_orders = [
            self.create_mock_order(order_id=_) for _ in ("294039830", "856939380")
        ]
        self.mock_CCAPI.get_orders_for_dispatch.return_value = mock_orders
        returned_value = models.Order.get_dispatched_orders()
        self.assertEqual(mock_orders, returned_value)
        self.mock_CCAPI.get_orders_for_dispatch.assert_called_once_with(
            order_type=1, number_of_days=1
        )
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 1)

    def test_get_dispatched_orders_number_of_days(self):
        mock_orders = [
            self.create_mock_order(order_id=_) for _ in ("294039830", "856939380")
        ]
        self.mock_CCAPI.get_orders_for_dispatch.return_value = mock_orders
        returned_value = models.Order.get_dispatched_orders(number_of_days=5)
        self.assertEqual(mock_orders, returned_value)
        self.mock_CCAPI.get_orders_for_dispatch.assert_called_once_with(
            order_type=1, number_of_days=5
        )
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 1)

    def test_update_sales(self):
        order = models.Order.objects.create(
            order_ID=self.order_ID, recieved=self.aware_tz(datetime(2019, 4, 3, 7, 23))
        )
        products = [
            self.create_mock_product(product_ID="3849390", quantity=1, price=6.50),
            self.create_mock_product(product_ID="5461616", quantity=5, price=12.80),
            self.create_mock_product(product_ID="9651664", quantity=3, price=0.99),
        ]
        mock_order = self.create_mock_order(order_id="939484393", products=products)
        models.Order.update_sales(order, mock_order)
        for product in products:
            self.assertTrue(
                models.ProductSale.objects.filter(
                    order=order, product_ID=product.id
                ).exists()
            )
            product_sale = models.ProductSale.objects.get(
                order=order, product_ID=product.id
            )
            self.assertEqual(product_sale.quantity, product.quantity)
            self.assertEqual(product_sale.price, int(product.price * 100))

    def test_update_sales_with_existing_record(self):
        order = models.Order.objects.create(
            order_ID=self.order_ID, recieved=self.aware_tz(datetime(2019, 4, 3, 7, 23))
        )
        products = [
            self.create_mock_product(product_ID="3849390", quantity=1, price=6.50),
            self.create_mock_product(product_ID="5461616", quantity=5, price=12.80),
            self.create_mock_product(product_ID="9651664", quantity=3, price=0.99),
        ]
        models.ProductSale.objects.create(
            order=order, product_ID=products[0].id, quantity=2, price=5.99
        )
        mock_order = self.create_mock_order(order_id="939484393", products=products)
        models.Order.update_sales(order, mock_order)
        for product in products:
            self.assertTrue(
                models.ProductSale.objects.filter(
                    order=order, product_ID=product.id
                ).exists()
            )
            product_sale = models.ProductSale.objects.get(
                order=order, product_ID=product.id
            )
            self.assertEqual(product_sale.quantity, product.quantity)
            self.assertEqual(product_sale.price, int(product.price * 100))

    def test_update(self):
        undispatched_order_IDs = ("39039340", "59403830")
        dispatched_order_IDs = ("294039830", "856939380")
        product_IDs = ("98119", "18919", "589191", "489191")
        products = (self.create_mock_product(product_ID=_) for _ in product_IDs)
        order_IDs = undispatched_order_IDs + dispatched_order_IDs
        undispatched_mock_orders = [
            self.create_mock_order(order_id=_, products=[next(products)])
            for _ in undispatched_order_IDs
        ]
        dispatched_mock_orders = [
            self.create_mock_order(order_id=_, products=[next(products)])
            for _ in dispatched_order_IDs
        ]
        for order_ID in order_IDs:
            self.assertFalse(models.Order.objects.filter(order_ID=order_ID).exists())
        self.mock_CCAPI.get_orders_for_dispatch.side_effect = [
            undispatched_mock_orders,
            dispatched_mock_orders,
        ]
        models.Order.update()
        for i, order_ID in enumerate(order_IDs):
            self.assertTrue(models.Order.objects.filter(order_ID=order_ID).exists())
            order = models.Order.objects.get(order_ID=order_ID)
            self.assertTrue(
                models.ProductSale.objects.filter(
                    order=order, product_ID=product_IDs[i]
                ).exists()
            )
        calls = (
            call(order_type=0, number_of_days=0),
            call(order_type=1, number_of_days=1),
        )
        self.mock_CCAPI.get_orders_for_dispatch.assert_has_calls(calls)
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 2)

    def test_product_sales_are_not_added_for_a_dispatched_order(self):
        self.assertFalse(models.Order.objects.filter(order_ID=self.order_ID).exists())
        recieved = self.aware_tz(datetime(2019, 4, 3, 7, 23))
        dispatched = self.aware_tz(datetime(2019, 4, 3, 12, 47))
        models.Order.objects.create(
            order_ID=self.order_ID, recieved=recieved, dispatched=dispatched
        )
        mock_product = self.create_mock_product()
        mock_order = self.create_mock_order(products=[mock_product])
        self.mock_CCAPI.get_orders_for_dispatch.side_effect = [[mock_order], []]
        models.Order.update()
        self.assertTrue(
            models.Order.objects.filter(order_ID=mock_order.order_id).exists()
        )
        order = models.Order.objects.get(order_ID=mock_order.order_id)
        self.assertFalse(
            models.ProductSale.objects.filter(
                order=order, product_ID=mock_product.id
            ).exists()
        )
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 2)


class TestProductSale(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/country",
        "shipping/services",
        "shipping/shipping_rules",
        "orders/channels",
        "orders/orders",
        "orders/product_sales",
    )

    def test_create_object(self):
        date = models.Order.make_tz_aware(
            datetime(year=2019, month=11, day=4, hour=13, minute=52)
        )
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
        date = models.Order.make_tz_aware(
            datetime(year=2019, month=11, day=4, hour=13, minute=52)
        )
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
