"""Find new Wowcher orders and add them to Cloud Commerce."""

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
            orders, errors = WowcherManager.get_new_orders()
        except Exception as e:
            logger.exception("Error getting new Wowcher orders.")
            raise e
        print(f"Added {len(orders)} Wowcher orders.", file=sys.stderr)
        if errors:
            for wowcher_code in errors:
                print(
                    f'Error creating order "{wowcher_code}" in Cloud Commerce.',
                    file=sys.stderr,
                )
            error_message = f"Failed to create {len(errors)} orders in Cloud Commerce."
            logger.exception(error_message)
            raise Exception(error_message)
