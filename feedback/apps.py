"""Config for Feedback app."""

from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    """Config for the Feedback app."""

    name = "feedback"
    verbose_name = "Feedback"
    create_group = True
