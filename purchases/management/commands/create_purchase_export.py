"""Create and email a monthly staff purchase report."""

import logging

from django.core.management.base import BaseCommand

from purchases.models import PurchaseExport

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Create and email a monthly staff purchase report."""

    help = """Create and email a monthly staff purchase report."""

    def handle(self, *args, **options):
        """Create a linnworks channel linking file."""
        try:
            export = PurchaseExport.objects.new_export()
        except Exception as e:
            logger.exception("Error creating staff purchase export.")
            raise e
        try:
            export.send_report_email()
        except Exception as e:
            logger.exception("Error sending staff purchase report email.")
            raise e
