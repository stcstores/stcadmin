"""
Barcode model.

Stores barcodes for use with new products.
"""
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone


class NotEnoughBarcodes(Exception):
    """Exception raised when there are not enough available barcodes."""

    def __init__(self):
        """Raise exception."""
        super().__init__("Not enough barcodes available.")


class BarcodeUsed(Exception):
    """Exception raised when marking a used barcode as used."""

    def __init__(self):
        """Raise exception."""
        super().__init__("Barcode is already used.")


class Barcode(models.Model):
    """Barcode for use with new products."""

    barcode = models.CharField(max_length=13, unique=True)
    available = models.BooleanField(default=True)
    added_on = models.DateTimeField(auto_now_add=True)
    used_on = models.DateTimeField(null=True)
    used_by = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    used_for = models.TextField(null=True)

    NotEnoughBarcodes = NotEnoughBarcodes
    BarcodeUsed = BarcodeUsed

    class Meta:
        """Meta class for Barcode."""

        verbose_name = "Barcode"
        verbose_name_plural = "Barcodes"

    def mark_used(self, user, used_for=None):
        """Mark barcode as used."""
        if not self.available:
            raise BarcodeUsed
        self.available = False
        self.used_on = timezone.now()
        self.used_by = user
        self.used_for = used_for
        self.save()

    @classmethod
    @transaction.atomic
    def get_barcode(cls, user, used_for=None):
        """Return and mark used a single barcode."""
        return cls.get_barcodes(count=1, user=user, used_for=used_for)[0]

    @classmethod
    @transaction.atomic
    def get_barcodes(cls, count, user, used_for=None):
        """Return and mark used a number of barcodes."""
        queryset = cls._default_manager.filter(available=True)[:count]
        if queryset.count() < count:
            raise NotEnoughBarcodes
        for barcode in queryset:
            barcode.mark_used(user, used_for=used_for)
        return [barcode.barcode for barcode in queryset]
