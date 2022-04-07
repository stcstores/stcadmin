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
            config = models.LinnworksConfig.get_solo()
            inventory_file = models.LinnworksProductImportFile.create()
            with open(config.inventory_import_file_path, "w") as f:
                inventory_file.write(f)
            composition_file = models.LinnworksCompostitionImportFile.create()
            with open(config.composition_import_file_path, "w") as f:
                composition_file.write(f)
        except Exception as e:
            logger.exception("Error creating Linnworks Product Import file.")
            raise e
