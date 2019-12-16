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

    @patch("monitor.views.now")
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


class TestFeedbackMonitorView(STCAdminTest, ViewTests):
    fixtures = (
        "home/cloud_commerce_user",
        "print_audit/cloud_commerce_order",
        "feedback/feedback",
        "feedback/user_feedback",
    )
    URL = "/monitor/feedback_monitor/"

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

    @patch("feedback.models.timezone.now")
    def test_response(self, mock_now):
        mock_now.return_value = datetime(2017, 7, 31)
        response = self.make_get_request()
        response_data = json.loads(response.content.decode("utf8"))
        self.assertIsInstance(response_data, dict)
        self.assertIn("total", response_data)
        self.assertIn("data", response_data)
        self.assertIsInstance(response_data["data"], list)
        for item in response_data["data"]:
            self.assertIsInstance(item, dict)
            self.assertIn("name", item)
            self.assertIsInstance(item["name"], str)
            self.assertIn("feedback", item)
            self.assertIsInstance(item["feedback"], list)
            for feedback in item["feedback"]:
                self.assertIn("name", feedback)
                self.assertIsInstance(feedback["name"], str)
                self.assertIn("image_url", feedback)
                self.assertIsInstance(feedback["image_url"], str)
                self.assertIn("ids", feedback)
                self.assertIsInstance(feedback["ids"], list)
                for id_item in feedback["ids"]:
                    self.assertIsInstance(id_item, int)
                self.assertIn("score", feedback)
                self.assertIsInstance(feedback["score"], int)
        expected_data = {
            "total": -32,
            "data": [
                {
                    "name": "Test User",
                    "feedback": [
                        {
                            "name": "Packing Mistake",
                            "image_url": "/media/feedback/packing_mistake.png",
                            "ids": [3, 5, 6, 15, 18],
                            "score": -2,
                        }
                    ],
                    "score": -10,
                },
                {
                    "name": " ",
                    "feedback": [
                        {
                            "name": "Packing Mistake",
                            "image_url": "/media/feedback/packing_mistake.png",
                            "ids": [1, 8, 9, 10, 11, 12, 13, 20, 26, 27, 29],
                            "score": -2,
                        }
                    ],
                    "score": -22,
                },
            ],
        }
        self.assertEqual(response_data, expected_data)
