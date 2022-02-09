"""Update Shopify Stock management command."""

import logging

from django.core.management.base import BaseCommand

from channels.models import ShopifyFulfillment

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Fulfill Shopify Orders command."""

    help = "Mark completed Shopify orders as fulfilled."

    def handle(self, *args, **options):
        """Mark completed Shopify orders as fulfilled."""
        try:
            ShopifyFulfillment.fulfill_completed_orders()
        except Exception as e:
            logger.exception("Error marking shopify orders fulfilled.")
            raise e
