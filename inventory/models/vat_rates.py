"""Model for VAT rates."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class VATRate(models.Model):
    """Model for VAT rates."""

    VAT_rate_ID = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50, unique=True)
    percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1)]
    )
    ordering = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        """Meta class for VAT Rate."""

        verbose_name = "VAT Rate"
        verbose_name_plural = "VAT Rates"
        ordering = ["ordering"]

    def __str__(self):
        return self.name
