"""Model for destinations recognised by Secured Mail."""

from django.db import models


class SecuredMailDestination(models.Model):
    """Secured Mail destinations."""

    name = models.CharField(max_length=255)
    manifest_row_number = models.PositiveIntegerField()

    class Meta:
        """Meta class for SecuredMailDestination."""

        verbose_name = 'Secured Mail Destination'
        verbose_name_plural = 'Secured Mail Destinations'

    def __str__(self):
        return self.name
