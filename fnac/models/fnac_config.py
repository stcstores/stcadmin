"""Fnac Config model."""
from django.db import models
from solo.models import SingletonModel

from inventory.models import Supplier


class FnacConfig(SingletonModel):
    """Model for FNAC config."""

    ignored_suppliers = models.ManyToManyField(Supplier, blank=True)
