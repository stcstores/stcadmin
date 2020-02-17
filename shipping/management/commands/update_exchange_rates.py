"""
Update Exchange Rates managment command.

Update the exchange rates in the shipping.Currency model.
"""

import logging

from django.core.management.base import BaseCommand

from shipping.models import Currency

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update orders models."""

    help = "Update currency exchange rates."

    def handle(self, *args, **options):
        """Update orders."""
        try:
            Currency.update()
        except Exception as e:
            logger.exception("Error updating currency exchange rates")
            raise e
