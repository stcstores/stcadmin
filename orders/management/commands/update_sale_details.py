"""
Update Sale Details management command.

Updates sales records with product details from Cloud Commerce.
"""

import logging

from django.core.management.base import BaseCommand

from orders.models import OrderDetailsUpdate

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update orders models."""

    help = "Update sales records with product details."

    def handle(self, *args, **options):
        """Update orders."""
        try:
            OrderDetailsUpdate.objects.start_update()
        except Exception as e:
            logger.exception("Error updating sale details")
            raise e
