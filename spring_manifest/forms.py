from django import forms
from spring_manifest import models


class UpdateOrderForm(forms.ModelForm):

    class Meta:
        model = models.SpringOrder
        fields = [
            'country', 'package_count', 'service']

    def save(self, commit=True):
        order = super().save(commit=False)
        if 'service' in self.changed_data:
            order.manifest = models.get_manifest_by_service(
                self.data['service'])
        if 'delay' in self.data:
            order.manifest = None
        elif 'cancel' in self.data:
            order.manifest = None
            order.canceled = True
        elif 'uncancel' or 'undelay' in self.data:
            if order.service == order.PACKET:
                order.manifest = models.get_manifest(
                    models.SpringManifest.UNTRACKED)
            else:
                order.manifest = models.get_manifest(
                    models.SpringManifest.TRACKED)
            order.canceled = False
        return super().save(commit=commit)
