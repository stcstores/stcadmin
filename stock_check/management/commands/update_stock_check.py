"""Update Stock Check management command."""

import sys

from django.core.management.base import BaseCommand
from stock_check import models
from tabler import XLSX, Table


class Command(BaseCommand):
    """
    Update Stock Check management command.

    Updates stock check database from a Cloud Commerce inventory export.

    Usage:
        python manage.py update_stock_check /path/to/export.csv
    """

    help = "Update Stock Check Database"

    def add_arguments(self, parser):
        """Add command argument."""
        parser.add_argument("inventory_file_path", type=str)

    def handle(self, *args, **options):
        """Update stock check database."""
        inventory_table_path = options.get("inventory_file_path")
        print(f"Updating stock locations from {inventory_table_path}", file=sys.stderr)
        inventory_table = Table(inventory_table_path, table_type=XLSX())
        models.update_stock_check(inventory_table)
