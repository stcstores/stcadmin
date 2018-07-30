"""FileManifestView class."""

import threading

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView
from spring_manifest import models
from spring_manifest.views import SpringUserMixin

from .securedmail import FileSecuredMailManifest


def file_manifest(manifest):
    """File manifest using appropriate FileManifest class."""
    if manifest.manifest_type.name == 'Secured Mail':
        FileSecuredMailManifest(manifest)
    else:
        raise Exception(
            'Unknown manifest type {} for manifest {}'.format(
                manifest.manifest_type, manifest.id))


class FileManifestView(SpringUserMixin, RedirectView):
    """File a manifest."""

    def get_manifest(self):
        """Return requested manifest."""
        manifest_id = self.kwargs['manifest_id']
        manifest = get_object_or_404(models.SpringManifest, pk=manifest_id)
        if manifest.status != manifest.FAILED and manifest.manifest_file:
            return None
        return manifest

    def process_manifest(self):
        """Set manifest as in progress and start thread to file it."""
        models.update_spring_orders()
        manifest = self.get_manifest()
        if manifest is not None:
            manifest.status = manifest.IN_PROGRESS
            manifest.errors = ''
            manifest.save()
            t = threading.Thread(target=file_manifest, args=[manifest])
            t.setDaemon(True)
            t.start()
        else:
            messages.add_message(
                self.request, messages.ERROR, 'Manifest already filed.')

    def get_redirect_url(self, *args, **kwargs):
        """Return URL to redirect to after manifest process starts."""
        self.process_manifest()
        return reverse_lazy(
            'spring_manifest:manifest',
            kwargs={'manifest_id': self.kwargs['manifest_id']})
