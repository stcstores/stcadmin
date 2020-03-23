"""
Update the inventory information used to manage FNAC.

Command: python manage.py update_fnac_inventory
"""

import logging

from django.core.management.base import BaseCommand

from fnac.models import update_inventory

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update the FNAC inventory."""

    help = "Update the FNAC inventory."

    def handle(self, *args, **kwargs):
        """Update the FNAC inventory."""
        try:
            update_inventory()
        except Exception as e:
            logger.exception(f"Error updating FNAC inventory: {e}")
            raise e
