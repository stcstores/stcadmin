"""Model Admin for the Feedback app."""
from django.contrib import admin

from feedback import models


@admin.register(models.Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Model admin for Feedback model."""

    pass


@admin.register(models.UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    """Model admin for UserFeedback model."""

    list_display = ("user", "feedback_type", "timestamp")
