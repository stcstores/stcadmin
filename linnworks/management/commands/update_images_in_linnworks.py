"""Create a linnworks update files."""

import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from linnworks import models

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Create a linnworks image update file."""

    help = """Create a linnworks image update file."""

    def handle(self, *args, **options):
        """Create a linnworks update files."""
        try:
            config = models.LinnworksConfig.get_solo()
            image_update_file = models.linnworks_import_files.ImageUpdateFile.create()
            with open(config.image_import_file_path, "w") as f:
                image_update_file.write(f)
            config.last_image_update = timezone.now()
            config.save()
        except Exception as e:
            logger.exception("Error creating Linnworks Image Import file.")
            raise e
