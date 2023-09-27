"""Update archivable products."""

import logging

from django.core.management.base import BaseCommand

from inventory.models.archive import Archiver

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update archivable products."""

    help = """
    Sets products as archived if they are:
        - Not already archived.
        - End of Line.
        - Out of stock.
        - Not in any open FBA orders.
    """

    def handle(self, *args, **options):
        """Update archivable products."""
        try:
            Archiver.archive_products()
        except Exception as e:
            logger.exception("Error archiving products.")
            raise e
