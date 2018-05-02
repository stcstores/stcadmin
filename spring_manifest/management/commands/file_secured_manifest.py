"""Management command to file the Secured Mail manifest."""

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
        """File the Spring Tracked manifest."""
        print('Updating Orders...')
        models.update_spring_orders()
        manifest = models.get_manifest(models.SpringManifest.SECURED_MAIL)
        print('Filing Manifest {}...'.format(manifest))
        FileSecuredMailManifest(manifest)
        print('{} orders filed for {} at {}'.format(
            manifest.springorder_set.count(), manifest, manifest.time_filed))
