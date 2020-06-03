from datetime import date, datetime, timedelta
from unittest.mock import Mock, call, patch

import pytz
from django.utils.timezone import make_aware
from isoweek import Week

from home.models import CloudCommerceUser
from orders import models
from shipping import models as shipping_models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestChannel(STCAdminTest):
    fixtures = ("orders/channel",)

    def test_create_object(self):
        name = "Test Channel"
        channel = models.Channel.objects.create(name=name)
        self.assertEqual(name, channel.name)

    def test_str(self):
        channel = models.Channel.objects.get(id=1)
        self.assertEqual(channel.name, str(channel))


class TestUrgentSince(STCAdminTest):
    @patch("orders.models.order.timezone.now")
    def test_urgent_since_monday(self, mock_now):
        mock_now.return_value = make_aware(datetime(2019, 12, 23))
        self.assertEqual(
            make_aware(datetime(2019, 12, 20)), models.order.urgent_since()
        )

    @patch("orders.models.order.timezone.now")
    def test_urgent_since_tuesday(self, mock_now):
        mock_now.return_value = make_aware(datetime(2019, 12, 24))
        self.assertEqual(
            make_aware(datetime(2019, 12, 23)), models.order.urgent_since()
        )

    @patch("orders.models.order.timezone.now")
    def test_urgent_since_wednesday(self, mock_now):
        mock_now.return_value = make_aware(datetime(2019, 12, 25))
        self.assertEqual(
            make_aware(datetime(2019, 12, 24)), models.order.urgent_since()
        )

    @patch("orders.models.order.timezone.now")
    def test_urgent_since_thursday(self, mock_now):
        mock_now.return_value = make_aware(datetime(2019, 12, 26))
        self.assertEqual(
            make_aware(datetime(2019, 12, 25)), models.order.urgent_since()
        )

    @patch("orders.models.order.timezone.now")
    def test_urgent_since_friday(self, mock_now):
        mock_now.return_value = make_aware(datetime(2019, 12, 27))
        self.assertEqual(
            make_aware(datetime(2019, 12, 26)), models.order.urgent_since()
        )

    @patch("orders.models.order.timezone.now")
    def test_urgent_since_saturday(self, mock_now):
        mock_now.return_value = make_aware(datetime(2019, 12, 28))
        self.assertEqual(
            make_aware(datetime(2019, 12, 27)), models.order.urgent_since()
        )

    @patch("orders.models.order.timezone.now")
    def test_urgent_since_sunday(self, mock_now):
        mock_now.return_value = make_aware(datetime(2019, 12, 29))
        self.assertEqual(
            make_aware(datetime(2019, 12, 27)), models.order.urgent_since()
        )


class TestOrder(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/region",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
        "shipping/courier",
        "shipping/courier_service",
        "shipping/shipping_rule",
        "orders/channel",
        "orders/order",
    )

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("orders.models.order.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

        self.order_ID = "3849389383"
        self.customer_ID = "59403"
        self.recieved_at = datetime(2019, 11, 3, 12, 23)
        self.dispatched_at = datetime(2019, 11, 3, 13, 57)
        self.aware_recieved_at = self.aware_tz(self.recieved_at)
        self.aware_dispatched_at = self.aware_tz(self.dispatched_at)
        self.cancelled = False
        self.ignored = False
        self.channel = models.Channel.objects.create(name="Test Channel")
        self.channel_order_ID = "8504389BHF9393"
        self.country = shipping_models.Country.objects.get(id=1)
        self.shipping_rule = shipping_models.ShippingRule.objects.get(id=1)
        self.courier_service = self.shipping_rule.courier_service
        self.shipping_rule_name = " - ".join(
            (self.shipping_rule.name, self.shipping_rule.courier_service.name)
        )
        self.tracking_number = "ABC009008"
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
        tracking_code=None,
        products=None,
        can_process_order=None,
    ):
        if order_id is None:
            order_id = self.order_ID
        if customer_id is None:
            customer_id = self.customer_ID
        if date_recieved is None:
            date_recieved = self.recieved_at
        if dispatch_date is None:
            dispatch_date = self.dispatched_at
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
        if tracking_code is None:
            tracking_code = self.tracking_number
        if products is None:
            products = [self.create_mock_product()]
        if can_process_order is None:
            can_process_order = not self.ignored
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
            tracking_code=tracking_code,
            products=products,
            can_process_order=can_process_order,
        )

    def create_mock_product(self, product_ID=None, price=None, quantity=None):
        if product_ID is None:
            product_ID = self.product_ID
        if price is None:
            price = self.product_price
        if quantity is None:
            quantity = self.product_quantity
        return Mock(product_id=product_ID, price=price, quantity=quantity)

    def aware_tz(self, date):
        return make_aware(date, timezone=pytz.timezone("Europe/London"))

    def test_create_object(self):
        order = models.Order.objects.create(
            order_ID=self.order_ID,
            customer_ID=self.customer_ID,
            recieved_at=self.aware_recieved_at,
            dispatched_at=self.aware_dispatched_at,
            channel=self.channel,
            channel_order_ID=self.channel_order_ID,
            country=self.country,
            shipping_rule=self.shipping_rule,
            courier_service=self.courier_service,
        )
        self.assertEqual(self.order_ID, order.order_ID)
        self.assertEqual(self.customer_ID, order.customer_ID)
        self.assertEqual(self.aware_recieved_at, order.recieved_at)
        self.assertEqual(self.aware_dispatched_at, order.dispatched_at)
        self.assertEqual(self.channel, order.channel)
        self.assertEqual(self.channel_order_ID, order.channel_order_ID)
        self.assertEqual(self.country, order.country)
        self.assertEqual(self.shipping_rule, order.shipping_rule)
        self.assertEqual(self.courier_service, order.courier_service)
        self.assertIsNone(order.tracking_number)
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)
        self.assertFalse(order.cancelled)
        self.assertFalse(order.ignored)

    def test_str(self):
        order = models.Order.objects.get(id=1)
        self.assertEqual(f"Order: {order.order_ID}", str(order))

    def test_is_dispatched(self):
        undispatched_order = models.Order.objects.get(id=1)
        self.assertIsNone(undispatched_order.dispatched_at)
        self.assertFalse(undispatched_order.is_dispatched())
        dispatched_order = models.Order.objects.filter(dispatched_at__isnull=False)[0]
        self.assertIsNotNone(dispatched_order.dispatched_at)
        self.assertTrue(dispatched_order.is_dispatched())

    def test_order_details(self):
        order = self.create_mock_order()
        order_details = models.Order.objects._cc_order_details(order)
        self.assertIsInstance(order_details, dict)
        self.assertIn("order_ID", order_details)
        self.assertEqual(self.order_ID, order_details["order_ID"])
        self.assertIn("customer_ID", order_details)
        self.assertEqual(self.customer_ID, order_details["customer_ID"])
        self.assertIn("recieved_at", order_details)
        self.assertEqual(self.aware_tz(self.recieved_at), order_details["recieved_at"])
        self.assertIn("dispatched_at", order_details)
        self.assertEqual(
            self.aware_tz(self.dispatched_at), order_details["dispatched_at"]
        )
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
        self.assertIn("courier_service", order_details)
        self.assertEqual(self.courier_service, order_details["courier_service"])
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)
        self.assertIn("tracking_number", order_details)
        self.assertEqual(self.tracking_number, order_details["tracking_number"])
        self.assertIn("ignored", order_details)
        self.assertEqual(self.ignored, order_details["ignored"])

    def test_parse_dispatch_date(self):
        self.assertEqual(
            self.aware_dispatched_at,
            models.Order.objects._parse_dispatch_date(self.dispatched_at),
        )
        self.assertIsNone(
            models.Order.objects._parse_dispatch_date(models.Order.DISPATCH_EPOCH)
        )
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test__get_shipping_rule(self):
        order = Mock(default_cs_rule_name=self.shipping_rule_name)
        self.assertEqual(
            self.shipping_rule, models.Order.objects._get_shipping_rule(order)
        )
        order = Mock(default_cs_rule_name="Non Existant Rule - Non Existant Service")
        self.assertIsNone(models.Order.objects._get_shipping_rule(order))
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_create_new_order(self):
        self.assertFalse(models.Order.objects.filter(order_ID=self.order_ID).exists())
        mock_order = self.create_mock_order()
        order = models.Order.objects._create_or_update_from_cc_order(mock_order)
        self.assertTrue(models.Order.objects.filter(order_ID=self.order_ID).exists())
        self.assertEqual(self.order_ID, order.order_ID)
        self.assertEqual(self.customer_ID, order.customer_ID)
        self.assertEqual(self.aware_recieved_at, order.recieved_at)
        self.assertEqual(self.aware_dispatched_at, order.dispatched_at)
        self.assertEqual(self.channel, order.channel)
        self.assertEqual(self.channel_order_ID, order.channel_order_ID)
        self.assertEqual(self.country, order.country)
        self.assertEqual(self.shipping_rule, order.shipping_rule)
        self.assertEqual(self.courier_service, order.courier_service)
        self.assertEqual(self.tracking_number, order.tracking_number)
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_update_order(self):
        self.assertFalse(models.Order.objects.filter(order_ID=self.order_ID).exists())
        models.Order.objects.create(
            order_ID=self.order_ID,
            recieved_at=self.aware_tz(datetime(2019, 4, 3, 7, 23)),
        )
        mock_order = self.create_mock_order()
        order = models.Order.objects._create_or_update_from_cc_order(mock_order)
        self.assertEqual(self.order_ID, order.order_ID)
        self.assertEqual(self.customer_ID, order.customer_ID)
        self.assertEqual(self.aware_recieved_at, order.recieved_at)
        self.assertEqual(self.aware_dispatched_at, order.dispatched_at)
        self.assertEqual(self.channel, order.channel)
        self.assertEqual(self.channel_order_ID, order.channel_order_ID)
        self.assertEqual(self.country, order.country)
        self.assertEqual(self.shipping_rule, order.shipping_rule)
        self.assertEqual(self.courier_service, order.courier_service)
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_dispatched_order_does_not_update(self):
        self.assertFalse(models.Order.objects.filter(order_ID=self.order_ID).exists())
        recieved_at = self.aware_tz(datetime(2019, 4, 3, 7, 23))
        dispatched_at = self.aware_tz(datetime(2019, 4, 3, 12, 47))
        models.Order.objects.create(
            order_ID=self.order_ID, recieved_at=recieved_at, dispatched_at=dispatched_at
        )
        mock_order = self.create_mock_order()
        returned_value = models.Order.objects._create_or_update_from_cc_order(
            mock_order
        )
        self.assertIsNone(returned_value)
        order = models.Order.objects.get(order_ID=self.order_ID)
        self.assertEqual(self.order_ID, order.order_ID)
        self.assertIsNone(order.customer_ID)
        self.assertEqual(recieved_at, order.recieved_at)
        self.assertEqual(dispatched_at, order.dispatched_at)
        self.assertIsNone(order.channel)
        self.assertIsNone(order.channel_order_ID)
        self.assertIsNone(order.country)
        self.assertIsNone(order.shipping_rule)
        self.assertIsNone(order.courier_service)
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 0)

    def test_invalid_country_code(self):
        mock_order = self.create_mock_order(delivery_country_code=9999)
        with self.assertRaises(models.Order.CountryNotRecognisedError):
            models.Order.objects._create_or_update_from_cc_order(mock_order)

    def test_invalid_shipping_rule(self):
        mock_order = self.create_mock_order(default_cs_rule_name="Invalid Rule Name")
        order = models.Order.objects._create_or_update_from_cc_order(mock_order)
        self.assertIsNone(order.shipping_rule)
        self.assertIsNone(order.courier_service)

    def test_get_orders_for_dispatch(self):
        mock_orders = [
            self.create_mock_order(order_id=_) for _ in ("294039830", "856939380")
        ]
        self.mock_CCAPI.get_orders_for_dispatch.return_value = mock_orders
        returned_value = models.Order.objects._get_orders_for_dispatch()
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
        returned_value = models.Order.objects._get_dispatched_orders()
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
        returned_value = models.Order.objects._get_dispatched_orders(number_of_days=5)
        self.assertEqual(mock_orders, returned_value)
        self.mock_CCAPI.get_orders_for_dispatch.assert_called_once_with(
            order_type=1, number_of_days=5
        )
        self.assertEqual(len(self.mock_CCAPI.mock_calls), 1)

    def test_update_sales(self):
        order = models.Order.objects.create(
            order_ID=self.order_ID,
            recieved_at=self.aware_tz(datetime(2019, 4, 3, 7, 23)),
        )
        products = [
            self.create_mock_product(product_ID="3849390", quantity=1, price=6.50),
            self.create_mock_product(product_ID="5461616", quantity=5, price=12.80),
            self.create_mock_product(product_ID="9651664", quantity=3, price=0.99),
        ]
        mock_order = self.create_mock_order(order_id="939484393", products=products)
        models.Order.objects._update_sales(order, mock_order)
        for product in products:
            self.assertTrue(
                models.ProductSale.objects.filter(
                    order=order, product_ID=product.product_id
                ).exists()
            )
            product_sale = models.ProductSale.objects.get(
                order=order, product_ID=product.product_id
            )
            self.assertEqual(product_sale.quantity, product.quantity)
            self.assertEqual(product_sale.price, int(product.price * 100))

    def test_update_sales_with_existing_record(self):
        order = models.Order.objects.create(
            order_ID=self.order_ID,
            recieved_at=self.aware_tz(datetime(2019, 4, 3, 7, 23)),
        )
        products = [
            self.create_mock_product(product_ID="3849390", quantity=1, price=6.50),
            self.create_mock_product(product_ID="5461616", quantity=5, price=12.80),
            self.create_mock_product(product_ID="9651664", quantity=3, price=0.99),
        ]
        models.ProductSale.objects.create(
            order=order, product_ID=products[0].product_id, quantity=2, price=5.99
        )
        mock_order = self.create_mock_order(order_id="939484393", products=products)
        models.Order.objects._update_sales(order, mock_order)
        for product in products:
            self.assertTrue(
                models.ProductSale.objects.filter(
                    order=order, product_ID=product.product_id
                ).exists()
            )
            product_sale = models.ProductSale.objects.get(
                order=order, product_ID=product.product_id
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
        self.mock_CCAPI.recent_orders_for_customer.return_value = {}
        for order_ID in order_IDs:
            self.assertFalse(models.Order.objects.filter(order_ID=order_ID).exists())
        self.mock_CCAPI.get_orders_for_dispatch.side_effect = [
            undispatched_mock_orders,
            dispatched_mock_orders,
        ]
        models.Order.objects.update_orders()
        for i, order_ID in enumerate(order_IDs):
            self.assertTrue(models.Order.objects.filter(order_ID=order_ID).exists())
            order = models.Order.objects.get(order_ID=order_ID)
            self.assertTrue(
                models.ProductSale.objects.filter(
                    order=order, product_ID=product_IDs[i]
                ).exists()
            )
        get_orders_calls = [
            call(order_type=0, number_of_days=0),
            call(order_type=1, number_of_days=1),
        ]
        self.mock_CCAPI.get_orders_for_dispatch.assert_has_calls(get_orders_calls)
        recent_orders_calls = [
            call(customer_ID=order.customer_ID)
            for order in models.Order.objects.filter(
                dispatched_at__isnull=True, cancelled=False, ignored=False
            )
        ]
        self.mock_CCAPI.recent_orders_for_customer.assert_has_calls(recent_orders_calls)
        self.assertEqual(
            len(self.mock_CCAPI.mock_calls),
            len(get_orders_calls) + len(recent_orders_calls),
        )

    def test_product_sales_are_not_added_for_a_dispatched_order(self):
        self.assertFalse(models.Order.objects.filter(order_ID=self.order_ID).exists())
        recieved_at = self.aware_tz(datetime(2019, 4, 3, 7, 23))
        dispatched_at = self.aware_tz(datetime(2019, 4, 3, 12, 47))
        models.Order.objects.create(
            order_ID=self.order_ID, recieved_at=recieved_at, dispatched_at=dispatched_at
        )
        mock_product = self.create_mock_product()
        mock_order = self.create_mock_order(products=[mock_product])
        self.mock_CCAPI.get_orders_for_dispatch.side_effect = [[mock_order], []]
        models.Order.objects.update_orders()
        self.assertTrue(
            models.Order.objects.filter(order_ID=mock_order.order_id).exists()
        )
        order = models.Order.objects.get(order_ID=mock_order.order_id)
        self.assertFalse(
            models.ProductSale.objects.filter(
                order=order, product_ID=mock_product.product_id
            ).exists()
        )

    def test_dispatched_manager(self):
        queryset = models.Order.objects.dispatched()
        self.assertEqual(11, queryset.count())
        for order in queryset:
            self.assertTrue(order.is_dispatched())

    def test_undispatched_manager(self):
        queryset = models.Order.objects.undispatched()
        self.assertEqual(16, queryset.count())
        for order in queryset:
            self.assertFalse(order.is_dispatched())

    def test_priority_manager(self):
        queryset = models.Order.objects.priority()
        self.assertEqual(10, queryset.count())
        for order in queryset:
            self.assertTrue(order.shipping_rule.priority)

    def test_non_priority_manager(self):
        queryset = models.Order.objects.non_priority()
        self.assertEqual(18, queryset.count())
        for order in queryset:
            self.assertFalse(order.shipping_rule.priority)

    def test_undispatched_priority_manager(self):
        queryset = models.Order.objects.undispatched().priority()
        self.assertEqual(1, queryset.count())
        for order in queryset:
            self.assertTrue(order.shipping_rule.priority)
            self.assertIsNone(order.dispatched_at)

    def test_undispatched_non_priority_manager(self):
        queryset = models.Order.objects.undispatched().non_priority()
        self.assertEqual(15, queryset.count())
        for order in queryset:
            self.assertFalse(order.shipping_rule.priority)
            self.assertIsNone(order.dispatched_at)

    @patch("orders.models.order.timezone.now")
    def test_urgent_manager(self, mock_now):
        mock_now.return_value = make_aware(datetime(2019, 12, 4))
        queryset = models.Order.objects.urgent()
        self.assertEqual(2, queryset.count())
        for order in queryset:
            self.assertLessEqual(order.recieved_at, models.order.urgent_since())

    def test_check_cancelled_marks_cancelled(self):
        order = models.Order.objects.filter(
            cancelled=False, dispatched_at__isnull=True, customer_ID__isnull=False
        )[0]
        mock_recent_order = Mock(
            order_id=order.order_ID, CANCELLED="Cancelled", status="Cancelled"
        )
        self.mock_CCAPI.recent_orders_for_customer.return_value = {
            order.order_ID: mock_recent_order
        }
        order.check_cancelled()
        order.refresh_from_db()
        self.mock_CCAPI.recent_orders_for_customer.assert_called_once_with(
            customer_ID=order.customer_ID
        )
        self.assertTrue(order.cancelled)

    def test_check_cancelled_marks_ignored(self):
        order = models.Order.objects.filter(
            cancelled=False, dispatched_at__isnull=True, customer_ID__isnull=False
        )[0]
        mock_recent_order = Mock(
            order_id=order.order_ID, IGNORED="ignored", status="ignored"
        )
        self.mock_CCAPI.recent_orders_for_customer.return_value = {
            order.order_ID: mock_recent_order
        }
        order.check_cancelled()
        order.refresh_from_db()
        self.mock_CCAPI.recent_orders_for_customer.assert_called_once_with(
            customer_ID=order.customer_ID
        )
        self.assertTrue(order.ignored)

    def test_check_cancelled_with_no_customer_ID(self):
        order = models.Order.objects.filter(
            cancelled=False, dispatched_at__isnull=True, customer_ID__isnull=False
        )[0]
        mock_recent_order = Mock(
            order_id=order.order_ID, CANCELLED="Cancelled", status="Open"
        )
        self.mock_CCAPI.recent_orders_for_customer.return_value = {
            order.order_ID: mock_recent_order
        }
        order.check_cancelled()
        order.refresh_from_db()
        self.mock_CCAPI.recent_orders_for_customer.assert_called_once_with(
            customer_ID=order.customer_ID
        )
        self.assertFalse(order.cancelled)

    def test_check_cancelled_with_uncancelled_order(self):
        order = models.Order.objects.get(id=1)
        order.dispatched_at = None
        order.customer_ID = None
        order.cancelled = False
        order.ignored = False
        order.save()
        order.check_cancelled()
        self.assertEqual(0, len(self.mock_CCAPI.mock_calls))


class TestProductSale(STCAdminTest):
    fixtures = (
        "shipping/currency",
        "shipping/region",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
        "shipping/courier",
        "shipping/courier_service",
        "shipping/shipping_rule",
        "orders/channel",
        "orders/order",
        "orders/product_sale",
    )

    def test_create_object(self):
        date = make_aware(datetime(year=2019, month=11, day=4, hour=13, minute=52))
        order = models.Order.objects.create(order_ID="3849383", recieved_at=date)
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
    fixtures = (
        "home/cloud_commerce_user",
        "shipping/currency",
        "shipping/region",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
        "shipping/courier",
        "shipping/courier_service",
        "shipping/shipping_rule",
        "orders/channel",
        "orders/order",
        "orders/product_sale",
        "orders/packing_record",
    )

    def setUp(self):
        super().setUp()
        ccapi_patcher = patch("orders.models.packing_record.CCAPI")
        self.mock_CCAPI = ccapi_patcher.start()
        self.addCleanup(ccapi_patcher.stop)

    def test_create_object(self):
        self.create_user()
        date = make_aware(datetime(year=2019, month=11, day=4, hour=13, minute=52))
        order = models.Order.objects.create(order_ID="3849383", recieved_at=date)
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

    def test_update(self):
        order = models.Order.objects.dispatched()[0]
        models.Order.objects.exclude(id=order.id).delete()
        user = CloudCommerceUser.objects.all()[0]
        models.PackingRecord.objects.all().delete()
        mock_log = Mock(
            note=(
                "Order Dispatched - Date: 05/12/2019 11:08:51 "
                f"OrderID: {order.order_ID} Override: No"
            ),
            added_by_user_ID=user.user_id,
        )
        self.mock_CCAPI.customer_logs.return_value = [mock_log]
        models.PackingRecord.objects.update_packing_records()
        self.assertTrue(models.PackingRecord.objects.filter(order=order).exists())
        record = models.PackingRecord.objects.get(order=order)
        self.assertEqual(order, record.order)
        self.assertEqual(user, record.packed_by)
        self.mock_CCAPI.customer_logs.assert_called_once_with(order.customer_ID)
        self.assertEqual(1, len(self.mock_CCAPI.mock_calls))

    def test_orders_to_update(self):
        models.PackingRecord.objects.all().delete()
        orders = models.PackingRecord.objects._orders_to_update()
        self.assertEqual(11, len(orders))
        for order in orders:
            self.assertTrue(order.is_dispatched())
            self.assertIsNotNone(order.customer_ID)

    def test_orders_to_update_ignores_null_customer_ID(self):
        dispatched_orders = models.Order.objects.dispatched()
        invalid_order = dispatched_orders[1]
        invalid_order.customer_ID = None
        invalid_order.save()
        models.PackingRecord.objects.all().delete()
        orders = models.PackingRecord.objects._orders_to_update()
        for order in orders:
            self.assertTrue(order.is_dispatched())
            self.assertIsNotNone(order.customer_ID)
        self.assertEqual(10, len(orders))

    def test_orders_to_update_ignores_existing_records(self):
        dispatched_orders = models.Order.objects.dispatched()
        invalid_order = dispatched_orders[2]
        models.PackingRecord.objects.exclude(order__id=invalid_order.id).delete()
        self.assertEqual(1, models.PackingRecord.objects.count())
        orders = models.PackingRecord.objects._orders_to_update()
        for order in orders:
            self.assertTrue(order.is_dispatched())
            self.assertIsNotNone(order.customer_ID)
        self.assertEqual(10, len(orders))

    def test_update_order_with_no_logs(self):
        order = models.Order.objects.dispatched()[0]
        models.PackingRecord.objects.all().delete()
        self.mock_CCAPI.customer_logs.return_value = []
        models.PackingRecord.objects._update_order(order)
        self.assertFalse(models.PackingRecord.objects.exists())

    def test_update_order_with_no_dispatch_logs(self):
        order = models.Order.objects.dispatched()[0]
        models.PackingRecord.objects.all().delete()
        mock_log = Mock(
            note=(
                "Some Other Note - Date: 05/12/2019 11:08:51 "
                f"OrderID: {order.order_ID} Override: No"
            ),
            added_by_user_ID="4859483",
        )
        self.mock_CCAPI.customer_logs.return_value = [mock_log]
        models.PackingRecord.objects._update_order(order)
        self.assertFalse(models.PackingRecord.objects.exists())

    def test_update_order_with_new_packer(self):
        order = models.Order.objects.dispatched()[0]
        models.PackingRecord.objects.all().delete()
        new_user_ID = "32940383"
        self.assertFalse(CloudCommerceUser.objects.filter(user_id=new_user_ID).exists())
        mock_log = Mock(
            note=(
                "Order Dispatched - Date: 05/12/2019 11:08:51 "
                f"OrderID: {order.order_ID} Override: No"
            ),
            added_by_user_ID=new_user_ID,
        )
        self.mock_CCAPI.customer_logs.return_value = [mock_log]
        models.PackingRecord.objects._update_order(order)
        self.assertTrue(CloudCommerceUser.objects.filter(user_id=new_user_ID).exists())


class TestOrderUpdate(STCAdminTest):
    fixtures = ("orders/order_update",)

    def test_create_object(self):
        update = models.OrderUpdate.objects.create()
        self.assertEqual(update.IN_PROGRESS, update.status)
        self.assertIsNone(update.completed_at)
        self.assertIsInstance(update.started_at, datetime)

    def test_str(self):
        date = make_aware(datetime(2019, 12, 3, 12, 33, 27))
        update = models.OrderUpdate.objects.create(
            completed_at=date + timedelta(minutes=15),
            status=models.OrderUpdate.COMPLETE,
        )
        update.started_at = date
        update.save()
        date_string = date.strftime("%Y-%m-%d %H:%M:%S")
        expected = f"OrderUpdate {date_string} - Complete"
        self.assertEqual(str(update), expected)

    @patch("orders.models.update.Order")
    @patch("orders.models.update.PackingRecord")
    @patch("orders.models.update.timezone.now")
    def test_update(self, mock_now, mock_packing_record, mock_order):
        mock_date = make_aware(datetime(2019, 12, 10))
        mock_now.return_value = mock_date
        update = models.OrderUpdate.objects.start_order_update()
        update.refresh_from_db()
        self.assertEqual(update.COMPLETE, update.status)
        self.assertEqual(mock_date, update.completed_at)
        mock_packing_record.objects.update_packing_records.assert_called_once()
        mock_order.objects.update_orders.assert_called_once()

    @patch("orders.models.update.Order")
    @patch("orders.models.update.PackingRecord")
    @patch("orders.models.update.timezone.now")
    def test_update_order_error(self, mock_now, mock_packing_record, mock_order):
        mock_date = make_aware(datetime(2019, 12, 10))
        mock_now.return_value = mock_date
        mock_order.objects.update_orders.side_effect = Mock(
            side_effect=Exception("Test")
        )
        with self.assertRaises(Exception):
            models.OrderUpdate.objects.start_order_update()
        self.assertEqual(
            1,
            models.OrderUpdate.objects.filter(status=models.OrderUpdate.ERROR).count(),
        )
        update = models.OrderUpdate.objects.get(status=models.OrderUpdate.ERROR)
        self.assertEqual(update.ERROR, update.status)
        self.assertEqual(mock_date, update.completed_at)
        mock_packing_record.update.assert_not_called()

    @patch("orders.models.update.Order")
    @patch("orders.models.update.PackingRecord")
    @patch("orders.models.update.timezone.now")
    def test_update_packing_record_error(
        self, mock_now, mock_packing_record, mock_order
    ):
        self.assertFalse(
            models.OrderUpdate.objects.filter(status=models.OrderUpdate.ERROR).exists()
        )
        mock_date = make_aware(datetime(2019, 12, 10))
        mock_now.return_value = mock_date
        mock_packing_record.objects.update_packing_records.side_effect = Mock(
            side_effect=Exception("Test")
        )
        with self.assertRaises(Exception):
            models.OrderUpdate.objects.start_order_update()
        self.assertEqual(
            1,
            models.OrderUpdate.objects.filter(status=models.OrderUpdate.ERROR).count(),
        )
        update = models.OrderUpdate.objects.get(status=models.OrderUpdate.ERROR)
        self.assertEqual(update.ERROR, update.status)
        self.assertEqual(mock_date, update.completed_at)
        mock_order.objects.update_orders.assert_called_once()
        mock_packing_record.objects.update_packing_records.assert_called_once()

    @patch("orders.models.update.Order")
    @patch("orders.models.update.PackingRecord")
    def test_update_already_in_progress(self, mock_packing_record, mock_order):
        models.OrderUpdate.objects.create()
        self.assertTrue(models.OrderUpdate.objects.is_in_progress())
        with self.assertRaises(models.OrderUpdate.OrderUpdateInProgressError):
            models.OrderUpdate.objects.start_order_update()
        mock_order.objects.update_orders.assert_not_called()
        mock_packing_record.update.assert_not_called()

    @patch("orders.models.update.Order")
    @patch("orders.models.update.PackingRecord")
    def test_timeout(self, mock_packing_record, mock_order):
        update = models.OrderUpdate.objects.create(
            status=models.OrderUpdate.IN_PROGRESS
        )
        update.started_at -= timedelta(hours=2)
        update.save()
        models.OrderUpdate.objects.start_order_update()
        update.refresh_from_db()
        self.assertEqual(update.ERROR, update.status)
        mock_order.objects.update_orders.assert_called()
        mock_packing_record.objects.update_packing_records.assert_called()

    def test_is_in_progress(self):
        self.assertFalse(
            models.OrderUpdate.objects.filter(
                status=models.OrderUpdate.IN_PROGRESS
            ).exists()
        )
        self.assertFalse(models.OrderUpdate.objects.is_in_progress())
        update = models.OrderUpdate.objects.create()
        update.status = update.IN_PROGRESS
        update.save()
        self.assertTrue(models.OrderUpdate.objects.is_in_progress())

    def test_timeout_updates(self):
        update = models.OrderUpdate.objects.create(
            status=models.OrderUpdate.IN_PROGRESS
        )
        update.started_at -= timedelta(hours=2)
        update.save()
        models.OrderUpdate.objects._timeout_update()
        update.refresh_from_db()
        self.assertEqual(update.ERROR, update.status)
        update = models.OrderUpdate.objects.create(
            status=models.OrderUpdate.IN_PROGRESS
        )
        update.started_at -= timedelta(minutes=10)
        update.save()
        models.OrderUpdate.objects._timeout_update()
        update.refresh_from_db()
        self.assertEqual(update.IN_PROGRESS, update.status)


class TestBreakage(STCAdminTest):
    fixtures = ("home/cloud_commerce_user", "orders/breakage")

    def test_create_object(self):
        product_sku = "3TF-8BG-HB9"
        order_id = "384393282"
        note = "Item Broken"
        packer = CloudCommerceUser.objects.get(id=1)
        timestamp = make_aware(datetime(2019, 12, 3))
        breakage = models.Breakage.objects.create(
            product_sku=product_sku,
            order_id=order_id,
            note=note,
            packer=packer,
            timestamp=timestamp,
        )
        self.assertEqual(product_sku, breakage.product_sku)
        self.assertEqual(order_id, breakage.order_id)
        self.assertEqual(note, breakage.note)
        self.assertEqual(packer, breakage.packer)
        self.assertEqual(timestamp, breakage.timestamp)
        self.assertEqual("3TF-8BG-HB9 on order 384393282", str(breakage))


class TestOrdersByDayChart(STCAdminTest):
    fixtures = (
        "home/cloud_commerce_user",
        "shipping/currency",
        "shipping/region",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
        "shipping/courier",
        "shipping/courier_service",
        "shipping/shipping_rule",
        "orders/channel",
        "orders/order",
        "orders/product_sale",
        "orders/packing_record",
    )

    @patch("orders.models.charts.timezone.now")
    def test_labels(self, mock_now):
        mock_date = make_aware(datetime(2019, 12, 4))
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByDay()
        labels = chart.get_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(chart.DAYS_TO_DISPLAY, len(labels))
        self.assertEqual(mock_date.strftime("%a %d %b %Y"), labels[-1])
        self.assertEqual(
            (mock_date - timedelta(days=chart.DAYS_TO_DISPLAY - 1)).strftime(
                "%a %d %b %Y"
            ),
            labels[0],
        )

    @patch("orders.models.charts.timezone.now")
    def test_count_orders(self, mock_now):
        mock_date = make_aware(datetime(2019, 12, 4))
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByDay()
        orders = chart.count_orders()
        self.assertIsInstance(orders, dict)
        self.assertEqual(chart.DAYS_TO_DISPLAY, len(orders))
        self.assertEqual(mock_date.date(), list(orders.keys())[-1])
        self.assertEqual(
            (mock_date - timedelta(days=chart.DAYS_TO_DISPLAY - 1)).date(),
            list(orders.keys())[0],
        )
        for key, value in orders.items():
            self.assertIsInstance(key, date)
        self.assertEqual(8, orders[date(2019, 12, 3)])

    @patch("orders.models.charts.timezone.now")
    def test_datasets(self, mock_now):
        mock_date = make_aware(datetime(2019, 12, 4))
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByDay()
        datasets = chart.get_datasets()
        self.assertEqual(1, len(datasets))
        dataset = datasets[0]
        expected_data = [0 for i in range(chart.DAYS_TO_DISPLAY)]
        expected_data[28] = 1
        expected_data[58] = 8
        expected_data[59] = 2
        self.assertEqual(expected_data, dataset["data"])


class TestOrdersByWeekChart(STCAdminTest):
    fixtures = (
        "home/cloud_commerce_user",
        "shipping/currency",
        "shipping/region",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
        "shipping/courier",
        "shipping/courier_service",
        "shipping/shipping_rule",
        "orders/channel",
        "orders/order",
        "orders/product_sale",
        "orders/packing_record",
    )

    @patch("orders.models.charts.Week.thisweek")
    def test_labels(self, mock_now):
        mock_date = Week(2019, 50)
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByWeek(number_of_weeks=5)
        labels = chart.get_labels()
        self.assertEqual(
            [
                Week(2019, 45).monday().strftime("%d-%b-%Y %V"),
                Week(2019, 46).monday().strftime("%d-%b-%Y %V"),
                Week(2019, 47).monday().strftime("%d-%b-%Y %V"),
                Week(2019, 48).monday().strftime("%d-%b-%Y %V"),
                Week(2019, 49).monday().strftime("%d-%b-%Y %V"),
            ],
            labels,
        )

    @patch("orders.models.charts.Week.thisweek")
    def test_order_counts(self, mock_now):
        mock_date = Week(2019, 50)
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByWeek(number_of_weeks=5)
        order_counts = chart.get_order_counts(*chart.dates())
        self.assertDictEqual(
            {
                Week(2019, 45): 0,
                Week(2019, 46): 0,
                Week(2019, 47): 0,
                Week(2019, 48): 0,
                Week(2019, 49): 10,
            },
            order_counts,
        )

    @patch("orders.models.charts.Week.thisweek")
    def test_dataset(self, mock_now):
        mock_date = Week(2019, 50)
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByWeek(number_of_weeks=5)
        datasets = chart.get_datasets()
        self.assertEqual(1, len(datasets))
        dataset = datasets[0]
        self.assertEqual([0, 0, 0, 0, 10], dataset["data"])
