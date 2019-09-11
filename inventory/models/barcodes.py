"""
Barcode model.

Stores barcodes for use with new products.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Barcode(models.Model):
    """Barcode for use with new products."""

    barcode = models.CharField(max_length=13, unique=True)
    available = models.BooleanField(default=True)
    added_on = models.DateTimeField(auto_now_add=True)
    used_on = models.DateTimeField(null=True)
    used_by = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    used_for = models.TextField(null=True)

    class Meta:
        """Meta class for Barcode."""

        verbose_name = "Barcode"
        verbose_name_plural = "Barcodes"

    def mark_used(self, user, used_for=None):
        """Mark barcode as used."""
        self.available = False
        self.used_on = timezone.now()
        self.used_by = user
        self.used_for = used_for
        self.save()


def get_barcode():
    """Return unused barcode as a string and mark it as used."""
    barcode = Barcode.objects.filter(used=False).all()[0]
    barcode.used = True
    barcode.save()
    return barcode.barcode
