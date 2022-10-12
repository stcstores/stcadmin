"""Config for the Reports app."""

from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """Config for the Reports app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "reports"
    verbose_name = "Reports"
    create_group = True
