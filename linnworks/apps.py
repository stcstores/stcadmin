"""Config for the linnworks app."""

from django.apps import AppConfig


class LinnworksConfig(AppConfig):
    """Config for the linnworks app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "linnworks"
    verbose_name = "Linnworks"
    create_group = True
