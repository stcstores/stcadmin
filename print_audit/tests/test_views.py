from datetime import datetime
from unittest.mock import patch

from home.models import CloudCommerceUser
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class TestPackCountMonitorView(STCAdminTest, ViewTests):
    fixtures = ("home/cloud_commerce_user", "print_audit/cloud_commerce_order")
    URL = "/print_audit/pack_count_monitor/"

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

    @patch("print_audit.views.timezone.now")
    def test_response(self, mock_now):
        mock_now.return_value = datetime(2017, 8, 1)
        response = self.make_get_request()
        content = response.content.decode("utf8")
        for user in CloudCommerceUser.unhidden.all():
            self.assertIn(user.full_name(), content)
