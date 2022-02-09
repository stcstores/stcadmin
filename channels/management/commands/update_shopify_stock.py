"""Update Shopify Stock management command."""

import logging

from django.core.management.base import BaseCommand

from channels.models import ShopifyInventoryUpdater

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update Shopify Stock command."""

    help = "Update stock levels on Shopify and hide out of stock products."

    def handle(self, *args, **options):
        """Update stock levels on Shopify and hide out of stock products."""
        try:
            ShopifyInventoryUpdater.update_stock()
        except Exception as e:
            logger.exception("Error updating shopify stock.")
            raise e
