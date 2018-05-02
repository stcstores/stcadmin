"""Management command to file the Spring Unracked manifest."""
from django.core.management.base import BaseCommand

from spring_manifest import models
from spring_manifest.views.file_manifest import FileUntrackedManifest


class Command(BaseCommand):
    """
    Management command to file the Spring Unracked Manifest.

    Usage:
        python manage.py file_untracked_manifest
    """

    help = 'File Unracked Manifest'

    def handle(self, *args, **options):
        """File the Spring Unracked manifest."""
        print('Updating Orders...')
        models.update_spring_orders()
        manifest = models.get_manifest(models.SpringManifest.UNTRACKED)
        print('Filing Manifest {}...'.format(manifest))
        FileUntrackedManifest(manifest)
        print('{} orders filed for {} at {}'.format(
            manifest.springorder_set.count(), manifest, manifest.time_filed))
