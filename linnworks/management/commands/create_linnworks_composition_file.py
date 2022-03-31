"""Create a linnworks composition file."""

import logging

from django.core.management.base import BaseCommand

from linnworks.models import LinnworksCompostitionImportFile

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Create a linnworks composition file."""

    help = """Create a linnworks composition file."""

    def handle(self, *args, **options):
        """Create a linnworks composition file."""
        try:
            csv_file = LinnworksCompostitionImportFile.create()
            print(csv_file.to_string())
        except Exception as e:
            logger.exception("Error creating Linnworks Product Import file.")
            raise e
