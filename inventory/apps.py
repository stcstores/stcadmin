"""Config for Inventory app."""

from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """Config for Inventory app."""

    name = 'inventory'
    verbose_name = 'Inventory'
    create_group = True
