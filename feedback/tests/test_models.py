from datetime import datetime
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from feedback import models
from home.models import CloudCommerceUser
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestFeedback(STCAdminTest):
    fixtures = ("feedback/feedback",)

    def test_create_object(self):
        name = "New Feedback Type"
        score = 2
        image = SimpleUploadedFile("image.jpg", b"File contents")
        feedback = models.Feedback.objects.create(name=name, image=image, score=score)
        self.assertEqual(name, feedback.name)
        self.assertEqual(score, feedback.score)
        self.assertIn("image", feedback.image.name)

    def test_str(self):
        feedback = models.Feedback.objects.get(id=1)
        self.assertEqual(feedback.name, str(feedback))


class TestUserFeedback(STCAdminTest):
    fixtures = (
        "home/cloud_commerce_user",
        "feedback/feedback",
        "feedback/user_feedback",
    )

    def test_create_object(self):
        user = CloudCommerceUser.objects.get(id=1)
        feedback_type = models.Feedback.objects.get(id=1)
        order_id = "3849390"
        note = "A note about a mistake"
        feedback = models.UserFeedback.objects.create(
            user=user, feedback_type=feedback_type, order_id=order_id, note=note
        )
        self.assertEqual(user, feedback.user)
        self.assertEqual(feedback_type, feedback.feedback_type)
        self.assertEqual(order_id, feedback.order_id)
        self.assertEqual(note, feedback.note)
        self.assertIsInstance(feedback.timestamp, datetime)

    def test_str(self):
        feedback = models.UserFeedback.objects.get(id=1)
        self.assertEqual(
            f"{feedback.feedback_type.name} for {feedback.user.full_name()}",
            str(feedback),
        )

    def test_scored_queryset(self):
        queryset = models.UserFeedback.objects.all()
        total_score = queryset.score()
        expected_score = sum([_.feedback_type.score for _ in queryset])
        self.assertEqual(expected_score, total_score)
        queryset = models.UserFeedback.objects.filter(user__id=1)
        user_score = queryset.score()
        expected_score = sum([_.feedback_type.score for _ in queryset])
        self.assertEqual(expected_score, user_score)

    @patch("print_audit.models.timezone.now")
    def test_this_month_manager(self, mock_now):
        mock_time = timezone.make_aware(datetime(2018, 6, 12))
        mock_now.return_value = mock_time
        expected_objects = models.UserFeedback.objects.filter(
            timestamp__month=mock_time.month, timestamp__year=mock_time.year
        )
        returned_objects = models.UserFeedback.this_month.all()
        self.assertEqual(list(expected_objects), list(returned_objects))
