"""Create a linnworks update files."""

import logging

from django.core.management.base import BaseCommand

from linnworks import models

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update records of Linnworks internal GUID order references."""

    help = """Update records of Linnworks internal GUID order references."""

    def handle(self, *args, **options):
        """Update records of Linnworks internal GUID order references."""
        try:
            models.LinnworksOrder.objects.update_order_guids()
        except Exception as e:
            logger.exception("Error updating order GUIDs.")
            raise e
