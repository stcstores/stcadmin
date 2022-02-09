"""Update Shopify Stock management command."""

import logging

from django.core.management.base import BaseCommand

from channels.models import ShopifyOrderImporter

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Import Shopify Orders command."""

    help = "Import orders from Shopify to Cloud Commerce."

    def handle(self, *args, **options):
        """Import orders from Shopify to Cloud Commerce."""
        try:
            ShopifyOrderImporter.import_orders()
        except Exception as e:
            logger.exception("Error importing shopify orders.")
            raise e
