import math
from datetime import datetime
from unittest.mock import Mock, patch

from django.contrib.auth.models import Group
from django.db.models.query import QuerySet
from django.shortcuts import reverse
from django.utils import timezone

from feedback import forms, models, views
from home.models import CloudCommerceUser
from orders.models import PackingRecord
from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests


class FeedbackTest(STCAdminTest):
    group_name = "feedback"

    def setUp(self):
        self.create_user()
        group = Group.objects.get(name=self.group_name)
        group.user_set.add(self.user)
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)


class TestFeebackUserMixin(STCAdminTest):
    def setUp(self):
        self.create_user()
        self.add_group("feedback")
        self.login_user()

    def test_valid_group(self):
        view = views.UserInGroupMixin()
        view.groups = ["feedback"]
        view.request = Mock(user=self.user)
        self.assertTrue(view.test_func())

    def test_invalid_group(self):
        view = views.UserInGroupMixin()
        view.groups = ["labelmaker"]
        view.request = Mock(user=self.user)
        self.assertFalse(view.test_func())


class TestFeedbackQuickview(FeedbackTest, ViewTests):
    URL = "/feedback/feedback_quickview/"
    template = "feedback/feedback_quickview.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertIn(reverse("feedback:monitor"), str(response.content))

    def test_user_not_in_group_get(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_user_not_in_group_post(self):
        response = self.make_post_request()
        self.assertEqual(405, response.status_code)

    def test_logged_out_user_post(self):
        response = self.make_post_request()
        self.assertEqual(405, response.status_code)


class TestUserFeedback(FeedbackTest, ViewTests):
    URL = "/feedback/user_feedback/"
    template = "feedback/user_feedback.html"
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
        "feedback/feedback",
        "feedback/user_feedback",
    )

    def get_form_data(self):
        return {"dates": "today"}

    def make_post_request(self):
        return self.client.post(self.get_URL(), self.get_form_data())

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    @patch("feedback.forms.timezone.now")
    def test_content(self, mock_now):
        mock_date = timezone.make_aware(datetime(2019, 12, 3))
        mock_now.return_value = mock_date
        response = self.make_get_request()
        content = str(response.content)
        self.assertTrue(CloudCommerceUser.unhidden.exists())
        for user in CloudCommerceUser.unhidden.all():
            self.assertIn(user.full_name(), content)
            pack_count = PackingRecord.objects.filter(
                order__dispatched_at__year=mock_date.year,
                order__dispatched_at__month=mock_date.month,
                order__dispatched_at__day=mock_date.day,
                packed_by=user,
            ).count()
            self.assertIn(str(pack_count), content)

    @patch("feedback.forms.timezone.now")
    def test_context(self, mock_now):
        mock_date = timezone.make_aware(datetime(2019, 12, 3))
        mock_now.return_value = mock_date
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("users", response.context)
        users = response.context["users"]
        self.assertIsInstance(users, QuerySet)
        user_ids = CloudCommerceUser.unhidden.values_list("id", flat=True)
        context_ids = [user["id"] for user in users]
        self.assertCountEqual(user_ids, context_ids)
        self.assertEqual(3, len(users))
        for user in users:
            self.assertIn("feedback_counts", user)
            feedback_counts = user["feedback_counts"]
            self.assertIsInstance(feedback_counts, dict)
            self.assertEqual(models.Feedback.objects.count(), len(feedback_counts))
            for feedback in feedback_counts.values():
                self.assertIsInstance(feedback, dict)
                self.assertIn("pk", feedback)
                self.assertTrue(
                    models.Feedback.objects.filter(id=feedback["pk"]).exists()
                )
                feedback_obj = models.Feedback.objects.get(id=feedback["pk"])
                self.assertIn("name", feedback)
                self.assertEqual(feedback_obj.name, feedback["name"])
                self.assertIn("image_url", feedback)
                self.assertEqual(feedback_obj.image.url, feedback["image_url"])
                self.assertIn("count", feedback)
            self.assertIn("full_name", user)
            self.assertEqual(
                models.CloudCommerceUser.objects.get(id=user["id"]).full_name(),
                user["full_name"],
            )
            pack_count = PackingRecord.objects.filter(
                order__dispatched_at__year=mock_date.year,
                order__dispatched_at__month=mock_date.month,
                order__dispatched_at__day=mock_date.day,
                packed_by__id=user["id"],
            ).count()
            self.assertEqual(pack_count, user["pack_count"])
        self.assertIn("feedback_types", response.context)
        feedback_types = response.context["feedback_types"]
        self.assertIsInstance(feedback_types, QuerySet)
        for feedback_type in models.Feedback.objects.all():
            self.assertIn(feedback_type, feedback_types)
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], forms.FeedbackDateFilterForm)

    def test_today(self):
        response = self.client.get(
            self.URL,
            {forms.FeedbackDateFilterForm.DATES: forms.FeedbackDateFilterForm.TODAY},
        )
        self.assertEqual(200, response.status_code)

    def test_yesterday(self):
        response = self.client.get(
            self.URL,
            {
                forms.FeedbackDateFilterForm.DATES: forms.FeedbackDateFilterForm.YESTERDAY
            },
        )
        self.assertEqual(200, response.status_code)

    def test_this_week(self):
        response = self.client.get(
            self.URL,
            {
                forms.FeedbackDateFilterForm.DATES: forms.FeedbackDateFilterForm.THIS_WEEK
            },
        )
        self.assertEqual(200, response.status_code)

    def test_this_month(self):
        response = self.client.get(
            self.URL,
            {
                forms.FeedbackDateFilterForm.DATES: forms.FeedbackDateFilterForm.THIS_MONTH
            },
        )
        self.assertEqual(200, response.status_code)

    def test_last_month(self):
        response = self.client.get(
            self.URL,
            {
                forms.FeedbackDateFilterForm.DATES: forms.FeedbackDateFilterForm.LAST_MONTH
            },
        )
        self.assertEqual(200, response.status_code)

    def test_this_year(self):
        response = self.client.get(
            self.URL,
            {
                forms.FeedbackDateFilterForm.DATES: forms.FeedbackDateFilterForm.THIS_YEAR
            },
        )
        self.assertEqual(200, response.status_code)

    def test_custom(self):
        response = self.client.get(
            self.URL,
            {
                forms.FeedbackDateFilterForm.DATES: forms.FeedbackDateFilterForm.CUSTOM,
                forms.FeedbackDateFilterForm.DATE_FROM: "2019-09-07",
                forms.FeedbackDateFilterForm.DATE_TO: "2019-11-29",
            },
        )
        self.assertEqual(200, response.status_code)


class TestCreateUserFeedback(FeedbackTest, ViewTests):
    fixtures = ("home/cloud_commerce_user", "feedback/feedback")
    template = "feedback/user_feedback_form.html"

    def get_URL(self, user_ID=None):
        if user_ID is None:
            user_ID = 1
        return f"/feedback/create_feedback/{user_ID}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_post_method(self):
        self.assertFalse(
            models.UserFeedback.objects.filter(user__id=1, feedback_type__id=1).exists()
        )
        form_data = {
            "user": 1,
            "feedback_type": 1,
            "order_id": "3849393",
            "note": "A description",
            "timestamp": "2006-11-24",
        }
        response = self.client.post(self.get_URL(), form_data)
        self.assertRedirects(response, reverse("feedback:user_feedback"))
        self.assertTrue(
            models.UserFeedback.objects.filter(user__id=1, feedback_type__id=1).exists()
        )
        feedback = models.UserFeedback.objects.get(user__id=1, feedback_type__id=1)
        self.assertEqual(form_data["order_id"], feedback.order_id)
        self.assertEqual(form_data["note"], feedback.note)
        year, month, day = form_data["timestamp"].split("-")
        self.assertEqual(int(year), feedback.timestamp.year)
        self.assertEqual(int(month), feedback.timestamp.month)
        self.assertEqual(int(day), feedback.timestamp.day)

    def test_invalid_user_id(self):
        response = self.client.get(self.get_URL(user_ID=999))
        self.assertEqual(404, response.status_code)


class TestUpdateUserFeedback(FeedbackTest, ViewTests):
    fixtures = (
        "home/cloud_commerce_user",
        "feedback/feedback",
        "feedback/user_feedback",
    )
    template = "feedback/user_feedback_form.html"

    def get_URL(self, feedback_ID=None):
        if feedback_ID is None:
            feedback_ID = 1
        return f"/feedback/update_feedback/{feedback_ID}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_post_method(self):
        feedback = models.UserFeedback.objects.get(id=1)
        form_data = {
            "user": 1,
            "feedback_type": 1,
            "order_id": "3849393",
            "note": "A description",
            "timestamp": "2006-11-24",
        }
        response = self.client.post(self.get_URL(), form_data)
        self.assertRedirects(response, reverse("feedback:user_feedback"))
        self.assertTrue(
            models.UserFeedback.objects.filter(user__id=1, feedback_type__id=1).exists()
        )
        feedback.refresh_from_db()
        self.assertEqual(form_data["order_id"], feedback.order_id)
        self.assertEqual(form_data["note"], feedback.note)
        year, month, day = form_data["timestamp"].split("-")
        self.assertEqual(int(year), feedback.timestamp.year)
        self.assertEqual(int(month), feedback.timestamp.month)
        self.assertEqual(int(day), feedback.timestamp.day)

    def test_invalid_feedback_id(self):
        response = self.client.get(self.get_URL(feedback_ID=999))
        self.assertEqual(404, response.status_code)


class TestDeleteUserFeedback(FeedbackTest, ViewTests):
    fixtures = (
        "home/cloud_commerce_user",
        "feedback/feedback",
        "feedback/user_feedback",
    )
    template = "feedback/user_feedback_form.html"

    def get_URL(self, feedback_ID=None):
        if feedback_ID is None:
            feedback_ID = 1
        return f"/feedback/delete_feedback/{feedback_ID}/"

    def test_post_method(self):
        self.assertTrue(models.UserFeedback.objects.filter(id=1).exists())
        response = self.make_post_request()
        self.assertFalse(models.UserFeedback.objects.filter(id=1).exists())
        self.assertRedirects(response, reverse("feedback:user_feedback"))


class TestFeedbackList(FeedbackTest, ViewTests):
    fixtures = (
        "home/cloud_commerce_user",
        "feedback/feedback",
        "feedback/user_feedback",
    )
    template = "feedback/feedback_list.html"
    URL = "/feedback/feedback_list/"

    def get_form_data(self):
        user = CloudCommerceUser.objects.get(id=1)
        feedback_type = models.Feedback.objects.get(id=1)
        return {"user": user.id, "feedback": feedback_type.id, "paginate_by": 10}

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_context_with_no_parameters(self):
        response = self.make_get_request()
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("feedback_user", response.context)
        self.assertIsNone(response.context["feedback_user"])
        self.assertIn("feedback_type", response.context)
        self.assertIsNone(response.context["feedback_type"])
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], forms.FeedbackSearchForm)

    def test_context_with_GET_parameters(self):
        user = CloudCommerceUser.objects.get(id=1)
        feedback_type = models.Feedback.objects.get(id=1)
        response = self.client.get(
            self.URL, {"user_id": user.id, "feedback_id": feedback_type.id}
        )
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("feedback_user", response.context)
        self.assertEqual(user, response.context["feedback_user"])
        self.assertIn("feedback_type", response.context)
        self.assertEqual(feedback_type, response.context["feedback_type"])
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], forms.FeedbackSearchForm)
        self.assertIn("feedback_list", response.context)
        self.assertCountEqual(
            response.context["feedback_list"],
            list(models.UserFeedback.objects.filter(user__id=1, feedback_type__id=1)),
        )

    def test_page_number_too_large(self):
        response = self.client.get(self.get_URL(), {"paginate_by": 5, "page": 50})
        pages = math.ceil(models.UserFeedback.objects.count() / 5)
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertIn(f"Page {pages} of {pages}", str(response.content))

    def test_page_number_negative(self):
        response = self.client.get(self.get_URL(), {"paginate_by": 5, "page": -1})
        self.assertEqual(404, response.status_code)


class TestFeedbackDetails(FeedbackTest, ViewTests):
    fixtures = (
        "home/cloud_commerce_user",
        "feedback/feedback",
        "feedback/user_feedback",
    )
    template = "feedback/feedback_details.html"

    def get_URL(self, feedback_ID=None):
        if feedback_ID is None:
            feedback_ID = 1
        return f"/feedback/feedback_details/{feedback_ID}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)
        self.assertTrue(hasattr(response, "context"))
        self.assertIsNotNone(response.context)
        self.assertIn("feedback", response.context)
        self.assertEqual(
            models.UserFeedback.objects.get(id=1), response.context["feedback"]
        )


class TestFeedbackMonitorView(STCAdminTest, ViewTests):
    fixtures = (
        "home/cloud_commerce_user",
        "print_audit/cloud_commerce_order",
        "feedback/feedback",
        "feedback/user_feedback",
    )
    URL = "/feedback/monitor/"
    template = "feedback/monitor.html"

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
                self.assertIsInstance(item[0], models.Feedback)
                self.assertIsInstance(item[1], range)
                feedback_count = models.UserFeedback.objects.filter(
                    user=user,
                    feedback_type=item[0],
                    timestamp__year=mock_date.year,
                    timestamp__month=mock_date.month,
                ).count()
                self.assertEqual(feedback_count, len(list(item[1])))
            self.assertTrue(hasattr(user, "score"))
            self.assertIsInstance(user.score, int)
            user_feedback = models.UserFeedback.objects.filter(
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
        feedback = models.UserFeedback.objects.filter(
            user__hidden=False,
            timestamp__year=mock_date.year,
            timestamp__month=mock_date.month,
        )
        users = {_.user for _ in feedback}
        for user in users:
            self.assertIn(user.full_name(), content)
        self.assertIn("Total:", content)
        self.assertIn("-32", content)
