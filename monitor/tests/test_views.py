import json
from datetime import datetime
from unittest.mock import patch

from feedback.models import Feedback, UserFeedback
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


class TestFeedbackMonitorView(STCAdminTest, ViewTests):
    fixtures = (
        "home/cloud_commerce_user",
        "print_audit/cloud_commerce_order",
        "feedback/feedback",
        "feedback/user_feedback",
    )
    URL = "/monitor/feedback_monitor/"
    template = "monitor/feedback.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, self.template)

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
    def test_context(self, mock_now):
        mock_date = datetime(2017, 7, 31)
        mock_now.return_value = mock_date
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("users", response.context)
        users = response.context["users"]
        self.assertIsInstance(users, list)
        self.assertEqual(2, len(users))
        for user in users:
            self.assertTrue(hasattr(user, "feedback"))
            self.assertIsInstance(user.feedback, list)
            self.assertTrue(len(user.feedback) > 0)
            for item in user.feedback:
                self.assertIsInstance(item, tuple)
                self.assertEqual(2, len(item))
                self.assertIsInstance(item[0], Feedback)
                self.assertIsInstance(item[1], range)
                feedback_count = UserFeedback.objects.filter(
                    user=user,
                    feedback_type=item[0],
                    timestamp__year=mock_date.year,
                    timestamp__month=mock_date.month,
                ).count()
                self.assertEqual(feedback_count, len(list(item[1])))
            self.assertTrue(hasattr(user, "score"))
            self.assertIsInstance(user.score, int)
            user_feedback = UserFeedback.objects.filter(
                user=user,
                timestamp__year=mock_date.year,
                timestamp__month=mock_date.month,
            )
            expected_score = sum((_.feedback_type.score for _ in user_feedback))
            self.assertEqual(expected_score, user.score)
        self.assertIn("total", response.context)
        self.assertIsInstance(response.context["total"], int)
        self.assertEqual(-32, response.context["total"])

    @patch("feedback.models.timezone.now")
    def test_response(self, mock_now):
        mock_date = datetime(2017, 7, 31)
        mock_now.return_value = mock_date
        response = self.make_get_request()
        content = response.content.decode("utf8")
        feedback = UserFeedback.objects.filter(
            user__hidden=False,
            timestamp__year=mock_date.year,
            timestamp__month=mock_date.month,
        )
        users = {_.user for _ in feedback}
        for user in users:
            self.assertIn(user.full_name(), content)
        self.assertIn("Total:", content)
        self.assertIn("-32", content)
