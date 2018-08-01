"""Management command to file the Secured Mail manifest."""

import sys

from django.core.management.base import BaseCommand
from spring_manifest import models
from spring_manifest.views.file_manifest import FileSecuredMailManifest


class Command(BaseCommand):
    """
    Management command to file the Secured Mail Manifest.

    Usage:
        python manage.py file_secured_manifest
    """

    help = 'File Tracked Manifest'

    def handle(self, *args, **options):
        """File the Secured Mail manifest."""
        print('Updating Orders...', file=sys.stderr)
        models.update_manifest_orders()
        manifest = models.get_manifest(models.Manifest.SECURED_MAIL)
        print(f'Filing Manifest {manifest}...', file=sys.stderr)
        FileSecuredMailManifest(manifest)
        print(
            (
                f'{manifest.manifestorder_set.count()} orders filed for '
                '{manifest} at {manifest.time_filed}'),
            file=sys.stderr)
