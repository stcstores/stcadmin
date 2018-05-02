"""Management command to update manifest orders."""

from django.core.management.base import BaseCommand

from spring_manifest.models import update_spring_orders


class Command(BaseCommand):
    """
    Management command to update manifest orders.

    Usage:
        python manage.py update_spring
    """

    help = 'Update Spring Manifest Orders'

    def handle(self, *args, **options):
        """Update manifests."""
        update_spring_orders()
