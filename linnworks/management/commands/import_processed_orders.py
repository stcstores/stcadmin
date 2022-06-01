"""Create a linnworks update files."""

import logging

from django.core.management.base import BaseCommand

from linnworks import models

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Import processed orders from Linnworks export files."""

    help = """Import processed orders from Linnworks export files."""

    def handle(self, *args, **options):
        """Import processed orders from Linnworks export files."""
        try:
            models.OrderUpdater().update_orders()
        except Exception as e:
            logger.exception("Error updating processed orders.")
            raise e
