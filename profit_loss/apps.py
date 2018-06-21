"""Config for Profit/Loss app."""

from django.apps import AppConfig


class ProfitLossConfig(AppConfig):
    """Config for Profit/Loss app."""

    name = 'profit_loss'
    verbose_name = 'Profit/Loss'
    create_group = True
