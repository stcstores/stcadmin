"""Config for the Purchases app."""

from django.apps import AppConfig


class PurchasesConfig(AppConfig):
    """Config for the Purchases app."""

    name = "purchases"
    verbose_name = "Purchases"
    create_group = True
