from django import forms

from .manifest import TrackedManifest

from django.forms import modelformset_factory
from spring_manifest import models


class SpringManifestForm(forms.Form):

    def clean(self):
        super().clean()
        self.manifests = self.get_manifests()
        for manifest in self.manifests:
            for error in manifest.errors:
                self.add_error('', error)

    def get_manifests(self):
        return [TrackedManifest()]


CloudCommerceCountryIDFormSet = modelformset_factory(
    models.CloudCommerceCountryID,
    fields=('name', 'iso_code', 'zone'), extra=0)
