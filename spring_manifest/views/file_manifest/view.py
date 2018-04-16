import threading

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView
from spring_manifest import models
from spring_manifest.views import SpringUserMixin

from .tracked import FileTrackedManifest
from .untracked import FileUntrackedManifest
from .securedmail import FileSecuredMailManifest


def file_manifest(manifest):
    if manifest.manifest_type == manifest.UNTRACKED:
        FileUntrackedManifest(manifest)
    elif manifest.manifest_type == manifest.TRACKED:
        FileTrackedManifest(manifest)
    elif manifest.manifest_type == manifest.SECURED_MAIL:
        FileSecuredMailManifest(manifest)
    else:
        raise Exception(
            'Unknown manifest type {} for manifest {}'.format(
                manifest.manifest_type, manifest.id))


class FileManifestView(SpringUserMixin, RedirectView):

    def get_manifest(self):
        manifest_id = self.kwargs['manifest_id']
        manifest = get_object_or_404(
            models.SpringManifest, pk=manifest_id)
        if manifest.status != manifest.FAILED and manifest.manifest_file:
            messages.add_message(
                self.request, messages.ERROR, 'Manifest already filed.')
            return None
        return manifest

    def process_manifest(self):
        models.update_spring_orders()
        manifest = self.get_manifest()
        manifest.status = manifest.IN_PROGRESS
        manifest.errors = ''
        manifest.save()
        t = threading.Thread(target=file_manifest, args=[manifest])
        t.setDaemon(True)
        t.start()

    def get_redirect_url(self, *args, **kwargs):
        self.process_manifest()
        return reverse_lazy(
                'spring_manifest:manifest',
                kwargs={'manifest_id': self.kwargs['manifest_id']})
