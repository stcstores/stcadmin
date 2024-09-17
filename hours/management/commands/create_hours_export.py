"""Create and email a monthly staff hours report."""

import logging

from django.core.management.base import BaseCommand

from hours.models import HoursExport

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Create and email a monthly staff hours report."""

    help = """Create and email a monthly staff hours report."""

    def handle(self, *args, **options):
        """Create an hours report file."""
        try:
            export = HoursExport.objects.new_export()
        except Exception as e:
            logger.exception("Error creating staff hours export.")
            raise e
        try:
            export.send_report_email()
        except Exception as e:
            logger.exception("Error sending staff hours report email.")
            raise e
