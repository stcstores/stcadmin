"""Create a linnworks update files."""

import logging

from django.core.management.base import BaseCommand

from linnworks import models

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Create a linnworks update files."""

    help = """Create a linnworks update files."""

    def handle(self, *args, **options):
        """Create a linnworks update files."""
        try:
            update = models.StockLevelExportUpdate.objects.create_update()
        except Exception as e:
            logger.exception("Error creating stock update records.")
            raise e
        if update is None:
            logger.exception("No new stock level export to import.")
            raise Exception("No new stock level export to import.")
