from django import forms
from django.forms import modelformset_factory
from spring_manifest import models

from .manifest import TrackedManifest, UnTrackedManifest


class SpringManifestForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.download = None
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        self.manifests = self.get_manifests()
        for name, manifest in self.manifests.items():
            for error in manifest.errors:
                self.add_error('', error)

    def file_manifests(self):
        for name, manifest in self.manifests.items():
            manifest.file_manifest()
        if self.manifests['untracked']:
            if self.manifests['untracked'].download:
                self.download = self.manifests['untracked'].download

    def get_manifests(self):
        return {'tracked': TrackedManifest(), 'untracked': UnTrackedManifest()}


CloudCommerceCountryIDFormSet = modelformset_factory(
    models.CloudCommerceCountryID,
    fields=('name', 'iso_code', 'zone', 'valid_spring_destination'), extra=0)
