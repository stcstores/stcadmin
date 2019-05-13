"""Create and download a Cloud Commerce Pro product export."""

import logging
import sys

from django.core.management.base import BaseCommand

from wowcher.wowcher_management import WowcherManager

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Get Wowcher orders command."""

    help = "Find new Wowcher orders and add them to Cloud Commerce."

    def handle(self, *args, **options):
        """Find new Wowcher orders and add them to Cloud Commerce."""
        try:
            orders = WowcherManager.get_new_orders()
        except Exception as e:
            logger.exception("Error getting new Wowcher orders.")
            raise e
        print(f"Added {len(orders)} Wowcher orders.", file=sys.stderr)
