"""Create and download a Cloud Commerce Pro product export."""

import logging

from django.core.management.base import BaseCommand

from inventory.models import ProductExport

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Get Product Export command."""

    help = "Check integrity of product location database."

    def handle(self, *args, **options):
        """Check integity of bay database."""
        try:
            ProductExport.add_new_export_to_database()
        except Exception as e:
            logger.exception("Error retriving product export.")
            raise e
