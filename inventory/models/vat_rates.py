"""Model for VAT rates."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from orderable.models import Orderable


class VATRate(Orderable):
    """Model for VAT rates."""

    VAT_rate_ID = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, unique=True)
    percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1)]
    )

    class Meta(Orderable.Meta):
        """Meta class for VAT Rate."""

        verbose_name = "VAT Rate"
        verbose_name_plural = "VAT Rates"

    def __str__(self):
        return self.name
