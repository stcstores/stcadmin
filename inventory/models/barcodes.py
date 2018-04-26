"""
Barcode model.

Stores barcodes for use with new products.
"""

from django.db import models


class Barcode(models.Model):
    """Barcode for use with new products."""

    barcode = models.CharField(max_length=13, unique=True)
    used = models.BooleanField(default=False)

    def mark_used(self):
        """Mark barcode as used."""
        self.used = True
        self.save()


def get_barcode():
    """Return unused barcode as a string and mark it as used."""
    barcode = Barcode.objects.filter(used=False).all()[0]
    barcode.used = True
    barcode.save()
    return barcode.barcode
