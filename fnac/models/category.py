"""Model for FNAC categories."""

from django.db import models


class Category(models.Model):
    """Model for FNAC categories."""

    name = models.CharField(max_length=255)
    english = models.TextField(unique=True)
    french = models.TextField(unique=True)
    requires_colour = models.BooleanField(default=False)

    def __str__(self):
        return self.name or self.english
