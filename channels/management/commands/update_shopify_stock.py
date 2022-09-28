"""Update Shopify Stock management command."""

import logging

from django.core.management.base import BaseCommand

from channels.models.shopify_models import ShopifyStockManager

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update Shopify Stock command."""

    help = "Hide out of stock products on Shopify."

    def handle(self, *args, **options):
        """Hide out of stock products on Shopify."""
        try:
            ShopifyStockManager.update_out_of_stock()
        except Exception as e:
            logger.exception("Error updating shopify stock.")
            raise e
