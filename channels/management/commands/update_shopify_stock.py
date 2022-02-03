"""Update Shopify Stock management command."""

import logging

from django.core.management.base import BaseCommand

from channels.models import ShopifyInventoryUpdater

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Check Location Integrity command."""

    help = "Check integrity of product location database."

    def handle(self, *args, **options):
        """Check integity of bay database."""
        try:
            ShopifyInventoryUpdater.update_stock()
        except Exception as e:
            logger.exception("Error updating shopify stock.")
            raise e
