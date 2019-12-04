"""The Packing Record model."""
from django.db import models

from print_audit.models import CloudCommerceUser

from .order import Order


class PackingRecord(models.Model):
    """Model for order packing."""

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    packed_by = models.ForeignKey(CloudCommerceUser, on_delete=models.PROTECT)

    class Meta:
        """Meta class for the Packing model."""

        verbose_name = "Packing Record"
        verbose_name_plural = "Packing Records"
