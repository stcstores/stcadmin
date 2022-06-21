"""Create a linnworks update files."""

import logging

from django.core.management.base import BaseCommand

from linnworks import models

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update order packing records."""

    help = """Update order packing records."""

    def handle(self, *args, **options):
        """Update order packing records."""
        try:
            models.LinnworksOrder.objects.update_packing_records()
        except Exception as e:
            logger.exception("Error updating order GUIDs.")
            raise e
