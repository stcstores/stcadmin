"""Config for the orders app."""
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Config for the orders app."""

    name = "orders"
    verbose_name = "Orders"
    create_group = True
