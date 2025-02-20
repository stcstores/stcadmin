"""Config for the logs app."""

from django.apps import AppConfig


class LogsConfig(AppConfig):
    """Config for the logs app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "logs"
    verbose_name = "Logs"
    create_group = True
