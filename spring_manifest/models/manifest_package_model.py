"""ManifestPackage model."""

from django.db import models

from .manifest_order_model import ManifestOrder


class ManifestPackage(models.Model):
    """Model for packages used to complete orders."""

    package_number = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(ManifestOrder, on_delete=models.CASCADE)
    _items = None

    class Meta:
        """Meta class for the ManifestPackage model."""

        verbose_name = "Manifest Package"
        verbose_name_plural = "Manifest Packages"
        unique_together = ("package_number", "order")
        ordering = ("package_number",)

    def __str__(self):
        return self.package_id()

    def package_id(self):
        """Return unique string for package."""
        return "{}_{}".format(self.order.order_id, self.package_number)

    @property
    def items(self):
        """Return all items related to this package."""
        if self._items is None:
            self._items = self.manifestitem_set.filter(quantity__gt=0).all()
        return self._items

    @property
    def quantity(self):
        """Return the number of individual items in the package."""
        return sum([item.quantity for item in self.items])

    @property
    def weight(self):
        """Return the weight the package."""
        return sum([item.weight * item.quantity for item in self.items])
