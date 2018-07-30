"""ManifestType model."""

from django.db import models


class ManifestType(models.Model):
    """Model for manifested shipping services."""

    name = models.CharField(max_length=255)

    class Meta:
        """Meta class for the Service model."""

        verbose_name = 'Manifest Type'
        verbose_name_plural = 'Manifest Types'

    def __str__(self):
        return self.name
