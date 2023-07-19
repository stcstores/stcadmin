"""Create a linnworks inventory file."""

import logging

from django.core.management.base import BaseCommand

from linnworks.models import LinnworksProductImportFile

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Create a linnworks inventory file."""

    help = """Create a linnworks inventory file."""

    def handle(self, *args, **options):
        """Create a linnworks inventory file."""
        try:
            LinnworksProductImportFile.create()
        except Exception as e:
            logger.exception("Error creating Linnworks Product Import file.")
            raise e
