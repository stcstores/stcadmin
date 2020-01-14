from datetime import datetime
from unittest.mock import patch

from django.http import HttpResponseNotAllowed
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.html import escape
from isoweek import Week

from home.models import CloudCommerceUser
from orders import forms, models
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class OrderViewTest(STCAdminTest):
    group_name = "orders"

    def setUp(self):
        self.create_user()
        self.add_group("orders")
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)


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
        "shipping/country",
        "shipping/provider",
        "shipping/service",
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
        "shipping/country",
        "shipping/provider",
        "shipping/service",
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
        "shipping/country",
        "shipping/provider",
        "shipping/service",
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
        self.assertEqual(17, response.context["total"])
        self.assertIn("priority", response.context)
        self.assertIsInstance(response.context["priority"], list)
        self.assertEqual(0, len(response.context["priority"]))
        self.assertIn("non_priority", response.context)
        self.assertIsInstance(response.context["non_priority"], list)
        self.assertEqual(0, len(response.context["non_priority"]))
        self.assertIn("urgent", response.context)
        self.assertIsInstance(response.context["urgent"], list)
        self.assertEqual(17, len(response.context["urgent"]))

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
