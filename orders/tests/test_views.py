from datetime import datetime
from unittest.mock import patch

from django.utils import timezone

from home.models import CloudCommerceUser
from orders import models
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class TestPackCountMonitorView(STCAdminTest, ViewTests):
    fixtures = (
        "home/cloud_commerce_user",
        "shipping/currency",
        "shipping/country",
        "shipping/services",
        "shipping/shipping_rules",
        "orders/channels",
        "orders/orders",
        "orders/product_sales",
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
