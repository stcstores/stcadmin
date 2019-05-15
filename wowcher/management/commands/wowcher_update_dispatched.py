"""Update Wowcher orders that have been dispatched in Cloud Commerce."""

import logging
import sys

from django.core.management.base import BaseCommand

from wowcher.wowcher_management import WowcherManager

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update Wowcher orders that have been dispatched in Cloud Commerce."""

    help = "Update Wowcher orders that have been dispatched in Cloud Commerce."

    def handle(self, *args, **options):
        """Update Wowcher orders that have been dispatched in Cloud Commerce."""
        try:
            orders = WowcherManager.update_dispatched_orders()
        except Exception as e:
            logger.exception("Error updating dispatched Wowcher orders.")
            raise e
        print(f"Marked {len(orders)} Wowcher orders as dispatched.", file=sys.stderr)
