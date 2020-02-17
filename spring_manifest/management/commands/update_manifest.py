"""Management command to update manifest orders."""

import logging

from django.core.management.base import BaseCommand

from spring_manifest.models import update_manifest_orders

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """
    Management command to update manifest orders.

    Usage:
        python manage.py update_manifest
    """

    help = "Update Manifest Orders"

    def handle(self, *args, **options):
        """Update manifests."""
        try:
            update_manifest_orders()
        except Exception as e:
            logger.exception("Update Manifest Error.")
            raise e
