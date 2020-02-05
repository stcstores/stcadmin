"""Forms for manifest app."""

from django import forms

from spring_manifest import models


class UpdateOrderForm(forms.ModelForm):
    """Form for updating manifest orders."""

    class Meta:
        """Set model and fields."""

        model = models.ManifestOrder
        fields = ["country", "service"]

    def save(self, commit=True):
        """Update database."""
        order = super().save(commit=False)
        service = models.ManifestService.objects.get(id=self.data["service"])
        order.manifest = models.get_manifest_by_service(service)
        if "delay" in self.data:
            order.manifest = None
        elif "cancel" in self.data:
            order.manifest = None
            order.canceled = True
        elif "uncancel" in self.data or "undelay" in self.data:
            order.manifest = models.get_manifest_by_service(order.service)
            order.canceled = False
        return super().save(commit=commit)
