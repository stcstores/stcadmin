import json
from datetime import datetime
from unittest.mock import patch

from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class TestDisplayMonitorView(STCAdminTest, ViewTests):
    URL = "/monitor/"
    template = "monitor/monitor.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_logged_out_user_get(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_user_not_in_group_get(self):
        pass

    def test_user_not_in_group_post(self):
        pass

    def test_logged_out_user_post(self):
        response = self.make_post_request()
        self.assertEqual(405, response.status_code)


class TestPackCountMonitorView(STCAdminTest, ViewTests):
    fixtures = ("home/cloud_commerce_user", "print_audit/cloud_commerce_order")
    URL = "/monitor/pack_count_monitor/"

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

    @patch("monitor.views.timezone.now")
    def test_response(self, mock_now):
        mock_now.return_value = datetime(2017, 8, 1)
        response = self.make_get_request()
        response_data = json.loads(response.content.decode("utf8"))
        self.assertIsInstance(response_data, list)
        self.assertEqual(3, len(response_data))
        for item in response_data:
            self.assertIsInstance(item, list)
        expected_data = [[" ", 46], ["Test User", 26], [" ", 1]]
        self.assertEqual(expected_data, response_data)
