"""ManifestPackage model."""

from django.db import models

from .manifest_order_model import ManifestOrder


class ManifestPackage(models.Model):
    """Model for packages used to complete orders."""

    package_number = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(ManifestOrder, on_delete=models.CASCADE)

    class Meta:
        """Meta class for the ManifestPackage model."""

        verbose_name = "Manifest Package"
        verbose_name_plural = "Manifest Packages"
        unique_together = ("package_number", "order")
        ordering = ("package_number",)

    def package_id(self):
        """Return unique string for package."""
        return "{}_{}".format(self.order.order_id, self.package_number)

    def __str__(self):
        return self.package_id()
