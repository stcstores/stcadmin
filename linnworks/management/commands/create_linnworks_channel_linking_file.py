"""Create a linnworks inventory file."""

import logging
from pathlib import Path

from django.core.management.base import BaseCommand

from linnworks.models import LinnworksChannelMappingImportFile, LinnworksConfig

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Create a linnworks channel linking file."""

    help = """Create a linnworks channel linking file."""

    def handle(self, *args, **options):
        """Create a linnworks channel linking file."""
        try:
            csv_file = LinnworksChannelMappingImportFile.create()
            path = Path(LinnworksConfig.get_solo().channel_items_import_file_path)
            with open(path, "w", encoding="utf8") as f:
                csv_file.write(f)
        except Exception as e:
            logger.exception("Error creating Linnworks Chaannel Linking Import file.")
            raise e
