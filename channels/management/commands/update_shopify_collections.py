"""Update Shopify Collections management command."""

import logging

from django.core.management.base import BaseCommand

from channels.models.shopify_models import ShopifyCollection

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update Shopify collections command."""

    help = "Update the list of Shopify collections."

    def handle(self, *args, **options):
        """Update the list of Shopify collections."""
        try:
            ShopifyCollection.objects.update_collections()
        except Exception as e:
            logger.exception("Error updating shopify collections.")
            raise e
