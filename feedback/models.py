"""Models for the Feedback app."""

from django.db import models
from django.utils import timezone

from home.models import CloudCommerceUser


class Feedback(models.Model):
    """Model for feedback scores."""

    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to="feedback")
    score = models.IntegerField(default=0)

    class Meta:
        """Meta class for Feedback."""

        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def __str__(self):
        return self.name


class UserFeedbackMonthlyManager(models.Manager):
    """
    Manager for UserFeedback.

    Limits queries to feedback dated with in the current month.
    """

    def get_queryset(self):
        """Return QuerySet of User Feedback dated in the current month."""
        current_time = timezone.now()
        return (
            super()
            .get_queryset()
            .filter(
                timestamp__month=current_time.month, timestamp__year=current_time.year
            )
        )


class UserFeedback(models.Model):
    """Model to link CloudCommerceUser with Feedback."""

    user = models.ForeignKey(CloudCommerceUser, on_delete=models.CASCADE)
    feedback_type = models.ForeignKey(Feedback, on_delete=models.CASCADE)
    timestamp = models.DateField(default=timezone.now)
    order_id = models.CharField(max_length=10, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    objects = models.Manager()
    this_month = UserFeedbackMonthlyManager()

    class Meta:
        """Meta class for UserFeedback."""

        verbose_name = "User Feedback"
        verbose_name_plural = "User Feedback"

    def __str__(self):
        return "{} for {}".format(self.feedback_type.name, self.user.full_name())
