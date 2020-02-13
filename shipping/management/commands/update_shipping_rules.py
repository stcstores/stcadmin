"""
Update Shipping Rules management command.

Updates the shipping.ShippingRule model from Cloud Commerce.
"""

import logging

from django.core.management.base import BaseCommand

from shipping.models import ShippingRule

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update orders models."""

    help = "Update shipping rules and courier services."

    def handle(self, *args, **options):
        """Update shipping rules."""
        try:
            ShippingRule.update()
        except Exception as e:
            logger.exception("Error updating Shipping Rules")
            raise e
