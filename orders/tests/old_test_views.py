import csv
import io
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from django.http import HttpResponseNotAllowed
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import escape
from django.utils.timezone import make_aware
from isoweek import Week

from home.models import CloudCommerceUser
from orders import forms, models, views
from shipping.models import Country
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class OrderViewTest(STCAdminTest):
    group_name = "orders"

    def setUp(self):
        self.create_user()
        self.add_group("orders")
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)


class TestSectionNavigation(STCAdminTest):
    links = [
        ("Orders", "orders:index"),
        ("Breakages", "orders:breakages"),
        ("Charts", "orders:charts"),
        ("Undispatched Orders", "orders:undispatched_orders"),
        ("Order List", "orders:order_list"),
    ]

    def test_links(self):
        content = render_to_string("orders/section_navigation.html")
        self.assertIn('<div class="section_navigation">', content)
        links = [
            f'<a href="{reverse(viewname)}">{text}</a>' for text, viewname in self.links
        ]
        for link in links:
            self.assertIn(link, content)


class TestIndexView(OrderViewTest, ViewTests):
    URL = "/orders/"
    template = "orders/index.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)


class TestPackCountMonitorView(STCAdminTest, ViewTests):
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
    URL = "/orders/pack_count_monitor/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)

    def test_logged_out_user_get(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)

    def test_user_not_in_group_get(self):
        pass

    def test_user_not_in_group_post(self):
        pass

    def test_logged_out_user_post(self):
        response = self.make_post_request()
        self.assertEqual(405, response.status_code)

    @patch("orders.views.timezone.now")
    def test_response(self, mock_now):
        mock_date = timezone.make_aware(datetime(2019, 12, 3))
        mock_now.return_value = mock_date
        response = self.make_get_request()
        content = response.content.decode("utf8")
        user_IDs = models.PackingRecord.objects.filter(
            order__dispatched_at__year=mock_date.year,
            order__dispatched_at__month=mock_date.month,
            order__dispatched_at__day=mock_date.day,
        ).values_list("packed_by", flat=True)
        self.assertEqual(2, len(user_IDs))
        for user_ID in user_IDs:
            user = CloudCommerceUser.objects.get(id=user_ID)
            self.assertIn(user.full_name(), content)
            pack_count = models.PackingRecord.objects.filter(
                order__dispatched_at__year=mock_date.year,
                order__dispatched_at__month=mock_date.month,
                order__dispatched_at__day=mock_date.day,
                packed_by=user,
            ).count()
            self.assertIn(str(pack_count), content)


class TestBreakagesView(OrderViewTest, ViewTests):
    fixtures = ("home/cloud_commerce_user", "orders/breakage")

    URL = "/orders/breakages/"
    template = "orders/breakages.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("breakages", response.context)
        breakages = response.context["breakages"]
        self.assertCountEqual(list(breakages), list(models.Breakage.objects.all()))

    def test_content(self):
        response = self.make_get_request()
        content = response.content.decode("utf8")
        for breakage in models.Breakage.objects.all():
            self.assertIn(breakage.order_id, content)
            self.assertIn(breakage.product_sku, content)
            self.assertIn(escape(breakage.note), content)


class TestAddBreakageView(OrderViewTest, ViewTests):
    fixtures = ("home/cloud_commerce_user", "orders/breakage")
    URL = "/orders/add_breakage/"
    template = "orders/breakage_form.html"

    def get_form_data(self):
        return {
            "product_sku": "4HJ-UL4-9YT",
            "order_id": "0238490383",
            "note": "A breakage note",
            "packer": 2,
        }

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_post_method(self):
        form_data = self.get_form_data()
        self.assertFalse(
            models.Breakage.objects.filter(order_id=form_data["order_id"]).exists()
        )
        response = self.client.post(self.URL, form_data)
        self.assertRedirects(response, reverse("orders:breakages"))
        self.assertTrue(
            models.Breakage.objects.filter(order_id=form_data["order_id"]).exists()
        )
        breakage = models.Breakage.objects.get(order_id=form_data["order_id"])
        self.assertEqual(breakage.product_sku, form_data["product_sku"])
        self.assertEqual(breakage.order_id, form_data["order_id"])
        self.assertEqual(breakage.note, form_data["note"])
        self.assertEqual(breakage.packer.id, form_data["packer"])


class TestUpdateBreakageView(OrderViewTest, ViewTests):
    fixtures = ("home/cloud_commerce_user", "orders/breakage")
    template = "orders/breakage_form.html"

    def get_URL(self, breakage_ID=None):
        if breakage_ID is None:
            breakage_ID = 1
        return f"/orders/update_breakage/{breakage_ID}/"

    def get_form_data(self):
        return {
            "product_sku": "4HJ-UL4-9YT",
            "order_id": "0238490383",
            "note": "A breakage note",
            "packer": 2,
        }

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_content(self):
        response = self.make_get_request()
        breakage = models.Breakage.objects.get(id=1)
        content = response.content.decode("utf8")
        self.assertIn(breakage.product_sku, content)
        self.assertIn(breakage.order_id, content)
        self.assertIn(breakage.note, content)
        self.assertIn(breakage.packer.full_name(), content)

    def test_post_method(self):
        form_data = self.get_form_data()
        response = self.client.post(self.get_URL(), form_data)
        self.assertRedirects(response, reverse("orders:breakages"))
        breakage = models.Breakage.objects.get(id=1)
        self.assertEqual(breakage.product_sku, form_data["product_sku"])
        self.assertEqual(breakage.order_id, form_data["order_id"])
        self.assertEqual(breakage.note, form_data["note"])
        self.assertEqual(breakage.packer.id, form_data["packer"])


class TestDeleteBreakageView(OrderViewTest, ViewTests):
    fixtures = ("home/cloud_commerce_user", "orders/breakage")
    template = "orders/breakage_confirm_delete.html"

    def get_URL(self, breakage_ID=None):
        if breakage_ID is None:
            breakage_ID = 1
        return f"/orders/delete_breakage/{breakage_ID}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertTrue(models.Breakage.objects.filter(id=1).exists())

    def test_post_method(self):
        response = self.make_post_request()
        self.assertRedirects(response, reverse("orders:breakages"))
        self.assertFalse(models.Breakage.objects.filter(id=1).exists())


class TestChartsView(OrderViewTest, ViewTests):
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

    URL = "/orders/charts/"
    template = "orders/charts.html"

    @patch("orders.models.charts.Week.thisweek")
    @patch("orders.models.charts.timezone.now")
    def test_get_method(self, mock_now, mock_thisweek):
        mock_date = timezone.make_aware(datetime(2019, 12, 5))
        mock_now.return_value = mock_date
        mock_thisweek.return_value = Week(mock_date.year, mock_date.isocalendar()[1])
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    @patch("orders.models.charts.Week.thisweek")
    @patch("orders.models.charts.timezone.now")
    def test_context(self, mock_now, mock_thisweek):
        mock_date = timezone.make_aware(datetime(2019, 12, 5))
        mock_now.return_value = mock_date
        mock_thisweek.return_value = Week(mock_date.year, mock_date.isocalendar()[1])
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], forms.ChartSettingsForm)
        self.assertIn("orders_by_week_chart", response.context)
        self.assertIsInstance(
            response.context["orders_by_week_chart"], models.charts.OrdersByWeek
        )
        self.assertIn("orders_by_day_chart", response.context)
        self.assertIsInstance(
            response.context["orders_by_day_chart"], models.charts.OrdersByDay
        )

    @patch("orders.models.charts.Week.thisweek")
    @patch("orders.models.charts.timezone.now")
    def test_post_method(self, mock_now, mock_thisweek):
        mock_date = timezone.make_aware(datetime(2019, 12, 5))
        mock_now.return_value = mock_date
        mock_thisweek.return_value = Week(mock_date.year, mock_date.isocalendar()[1])
        response = self.client.post(self.URL, {"number_of_weeks": 5})
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertEqual(
            5, len(response.context["orders_by_week_chart"].get_datasets()[0]["data"])
        )


class TestUndispatchedDataView(OrderViewTest, ViewTests):
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

    URL = "/orders/undispatched_data/"
    template = "orders/undispatched_data.html"

    @patch("orders.models.charts.Week.thisweek")
    @patch("orders.models.charts.timezone.now")
    def test_get_method(self, mock_now, mock_thisweek):
        mock_date = timezone.make_aware(datetime(2019, 12, 5))
        mock_now.return_value = mock_date
        mock_thisweek.return_value = Week(mock_date.year, mock_date.isocalendar()[1])
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    @patch("orders.models.charts.Week.thisweek")
    @patch("orders.models.charts.timezone.now")
    def test_context(self, mock_now, mock_thisweek):
        mock_date = timezone.make_aware(datetime(2019, 12, 5))
        mock_now.return_value = mock_date
        mock_thisweek.return_value = Week(mock_date.year, mock_date.isocalendar()[1])
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("total", response.context)
        self.assertIsInstance(response.context["total"], int)
        self.assertEqual(16, response.context["total"])
        self.assertIn("priority", response.context)
        self.assertIsInstance(response.context["priority"], list)
        self.assertEqual(0, len(response.context["priority"]))
        self.assertIn("non_priority", response.context)
        self.assertIsInstance(response.context["non_priority"], list)
        self.assertEqual(0, len(response.context["non_priority"]))
        self.assertIn("urgent", response.context)
        self.assertIsInstance(response.context["urgent"], list)
        self.assertEqual(16, len(response.context["urgent"]))

    def test_user_not_in_group_get(self):
        self.remove_group()
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_logged_out_user_get(self):
        self.client.logout()
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

    def test_logged_out_user_post(self):
        self.client.logout()
        response = self.make_post_request()
        self.assertIsInstance(response, HttpResponseNotAllowed)

    def test_user_not_in_group_post(self):
        self.remove_group()
        response = self.make_post_request()
        self.assertIsInstance(response, HttpResponseNotAllowed)


class TestUndispatchedOrdersView(OrderViewTest, ViewTests):

    URL = "/orders/undispatched_orders/"
    template = "orders/undispatched.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)
        self.assertIn(reverse("orders:undispatched_data"), str(response.content))


class TestOrderListView(OrderViewTest, ViewTests):
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
    )

    URL = "/orders/order_list/"
    template = "orders/order_list.html"
    paginate_by = views.OrderList.paginate_by

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("object_list", response.context)

    def test_content(self):
        response = self.make_get_request()
        content = str(response.content)
        self.assertIn('<div class="section_navigation">', content)
        orders = models.Order.objects.dispatched().order_by("-recieved_at")[
            : self.paginate_by
        ]
        orders[0].tracking_number = "RM_7845938393"
        for order in orders:
            self.assertIn(order.order_ID, content)
            if order.tracking_number:
                self.assertIn(order.tracking_number, content)
            self.assertIn(order.shipping_rule.name, content)
            self.assertIn(order.recieved_at.strftime("%Y-%m-%d"), content)

    def test_filter_country(self):
        country = Country.objects.get(name="United Kingdom")
        response = self.client.get(self.URL, {"country": country.id})
        self.assertTrue(response.context["form"].is_valid())
        orders = response.context["object_list"]
        self.assertGreater(len(orders), 0)
        for order in orders:
            self.assertEqual(order.country, country)

    def test_filter_by_date(self):
        recieved_from = make_aware(datetime(2019, 12, 3))
        recieved_to = make_aware(datetime(2019, 12, 4))
        response = self.client.get(
            self.URL,
            {
                "recieved_from": recieved_from.strftime("%Y-%m-%d"),
                "recieved_to": recieved_to.strftime("%Y-%m-%d"),
            },
        )
        self.assertTrue(response.context["form"].is_valid())
        orders = response.context["object_list"]
        for order in orders:
            self.assertGreaterEqual(order.recieved_at, recieved_from)
            self.assertLessEqual(order.recieved_at, recieved_to + timedelta(days=1))

    def test_filter_by_order_id(self):
        order = models.Order.objects.dispatched()[0]
        response = self.client.get(self.URL, {"order_ID": order.order_ID})
        self.assertEqual(list(response.context["object_list"]), [order])

    def test_page_range(self):
        paginator = Mock(num_pages=5)
        self.assertEqual([1, 2, 3, 4, 5], views.OrderList().get_page_range(paginator))
        paginator.num_pages = 55
        self.assertEqual(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 55],
            views.OrderList().get_page_range(paginator),
        )

    def test_invalid_form(self):
        response = self.client.get(self.URL, {"country": 999999})
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertFalse(response.context["form"].is_valid())


class TestExportOrdersView(OrderViewTest, ViewTests):
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
    )

    URL = "/orders/export_orders/"

    def read_csv(self, response):
        rows = list(
            csv.reader(io.StringIO(response.content.decode("utf8")), delimiter=",")
        )
        return rows[0], rows[1:]

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        header, rows = self.read_csv(response)
        self.assertEqual(views.ExportOrders.header, header)
        self.assertEqual(models.Order.objects.dispatched().count(), len(rows))

    def test_filter_country(self):
        country = Country.objects.get(name="United Kingdom")
        response = self.client.get(self.URL, {"country": country.id})
        header, rows = self.read_csv(response)
        self.assertEqual(views.ExportOrders.header, header)
        self.assertEqual(
            models.Order.objects.dispatched().filter(country=country).count(), len(rows)
        )
        order = models.Order.objects.get(order_ID=rows[0][0])
        self.assertEqual(
            [
                order.order_ID,
                order.recieved_at.strftime("%Y-%m-%d"),
                order.country.name,
                order.channel.name,
                order.tracking_number,
                order.shipping_rule.name,
                order.courier_service.name,
            ],
            rows[0],
        )

    def test_filter_by_date(self):
        recieved_from = make_aware(datetime(2019, 12, 3))
        recieved_to = make_aware(datetime(2019, 12, 4))
        response = self.client.get(
            self.URL,
            {
                "recieved_from": recieved_from.strftime("%Y-%m-%d"),
                "recieved_to": recieved_to.strftime("%Y-%m-%d"),
            },
        )
        header, rows = self.read_csv(response)
        self.assertEqual(
            models.Order.objects.dispatched()
            .filter(
                recieved_at__gte=recieved_from,
                recieved_at__lte=recieved_to + timedelta(days=1),
            )
            .count(),
            len(rows),
        )

    def test_invalid_form(self):
        response = self.client.get(self.URL, {"country": 999999})
        self.assertEqual(404, response.status_code)
