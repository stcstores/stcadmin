"""Model for Spring destination zones."""

from django.db import models


class DestinationZone(models.Model):
    """Zones recognised by Spring."""

    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    format_code = models.CharField(
        max_length=1, blank=True, null=True, default=None)

    class Meta:
        """Sort by name."""

        ordering = ('name', )

    def safe_name(self):
        """Return name as a slug."""
        return self.name.lower().replace(' ', '_')

    def __str__(self):
        return str(self.name)
