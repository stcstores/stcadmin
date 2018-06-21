"""Config for EPOS app."""

from django.apps import AppConfig


class EposConfig(AppConfig):
    """Config for EPOS app."""

    name = 'epos'
    verbose_name = 'EPOS'
    create_group = True
