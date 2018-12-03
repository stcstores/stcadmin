"""Create and download a Cloud Commerce Pro product export."""

import logging
import sys
from pathlib import Path

from django.core.management.base import BaseCommand

from inventory.models import GetProductExport

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Get Product Export command."""

    help = "Check integrity of product location database."

    def add_arguments(self, parser):
        """Add command argument."""
        parser.add_argument("path", type=str, help="Path to export save location.")

    def handle(self, *args, **options):
        """Check integity of bay database."""
        try:
            path = Path(options.get("path")).absolute()
            print(f"Saving product export to {path}", file=sys.stderr)
            GetProductExport(path=path)
        except Exception as e:
            logger.exception("Error retriving product export.")
            raise e
