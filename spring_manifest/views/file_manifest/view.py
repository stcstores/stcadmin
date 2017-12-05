from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from spring_manifest import models
from spring_manifest.views import SpringUserMixin

from .tracked import FileTrackedManifest
from .untracked import FileUntrackedManifest


class FileManifestView(SpringUserMixin, RedirectView):

    def get_manifest(self):
        manifest_id = self.kwargs['manifest_id']
        manifest = get_object_or_404(
            models.SpringManifest, pk=manifest_id)
        if manifest.manifest_file:
            messages.add_message(
                self.request, messages.ERROR, 'Manifest already filed.')
            return None
        return manifest

    def process_manifest(self):
        models.update_spring_orders()
        manifest = self.get_manifest()
        if manifest is not None:
            if manifest.manifest_type == manifest.UNTRACKED:
                FileUntrackedManifest(manifest, request=self.request)
            elif manifest.manifest_type == manifest.TRACKED:
                FileTrackedManifest(manifest, request=self.request)
            else:
                raise Exception(
                    'Unknown manifest type {} for manifest {}'.format(
                        manifest.manifest_type, manifest.id))

    def get_redirect_url(self, *args, **kwargs):
        self.process_manifest()
        return reverse_lazy(
                'spring_manifest:manifest',
                kwargs={'manifest_id': self.kwargs['manifest_id']})
