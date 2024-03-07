"""Update FBA profit calculations."""

import logging

from django.core.management.base import BaseCommand

from fba.models import FBAProfitFile

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update FBA profit calculations."""

    help = """Update FBA profit calculations."""

    def handle(self, *args, **options):
        """Create a linnworks channel linking file."""
        try:
            FBAProfitFile.objects.update_from_exports()
        except Exception as e:
            logger.exception("Error updating FBA profit.")
            raise e
