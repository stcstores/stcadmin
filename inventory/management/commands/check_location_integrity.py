"""
Check location integrity management command.

Find discrepencies between STCAdmin bay database and Cloud Commerce bays.
Save results as .csv in media/logs.

Command: python management.py check_location_integrity.
"""

from django.core.management.base import BaseCommand

from inventory.models import check_location_integrity


class Command(BaseCommand):
    """Check Location Integrity command."""

    help = 'Check integrity of product location database.'

    def handle(self, *args, **options):
        """Check integity of bay database."""
        check_location_integrity()
