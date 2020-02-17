"""
Update profit loss management command.

Update profit loss database with current orders.

Usage:
    python manage.py update_profit_loss
"""

import logging

from django.core.management.base import BaseCommand

from profit_loss.models import UpdateOrderProfit

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """
    Update profit loss management command.

    Update profit loss database with current orders.

    Usage:
        python manage.py update_profit_loss
    """

    help = "Updates Print Audit"

    def handle(self, *args, **options):
        """Update profit loss database or log error."""
        try:
            UpdateOrderProfit()
        except Exception as e:
            logger.exception("Error updating profit/loss.")
            raise e
