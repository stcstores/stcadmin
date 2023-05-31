"""Config for the restock app."""

from django.apps import AppConfig


class RestockConfig(AppConfig):
    """Config for the restock app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "restock"
    verbose_name = "Restock"
