"""
Update Orders management command.

Updates the orders.Order and orders.PackingRecord models from Cloud Commerce.
"""

import logging

from django.core.management.base import BaseCommand

from shipping.models import Currency

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update orders models."""

    help = "Update orders and packing records."

    def handle(self, *args, **options):
        """Update orders."""
        try:
            Currency.update()
        except Exception as e:
            logger.exception("Error updating Orders")
            raise e
