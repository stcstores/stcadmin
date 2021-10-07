"""Update package tracking information."""

import logging

from django.core.management.base import BaseCommand

from tracking import models

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update orders models."""

    help = "Update orders and packing records."

    def handle(self, *args, **options):
        """Update orders."""
        try:
            models.TrackingAPI.update_tracking_information()
            models.TrackingStatus.update_tracking()
        except Exception as e:
            logger.exception("Error updating tracking.")
            raise e
