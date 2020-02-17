"""
Check location integrity management command.

Find discrepencies between STCAdmin bay database and Cloud Commerce bays.
Save results as .csv in media/logs.

Command: python management.py check_location_integrity.
"""

import logging

from django.core.management.base import BaseCommand

from inventory.models import check_location_integrity

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Check Location Integrity command."""

    help = "Check integrity of product location database."

    def handle(self, *args, **options):
        """Check integity of bay database."""
        try:
            check_location_integrity()
        except Exception as e:
            logger.exception("Error checking location intregrity.")
            raise e
