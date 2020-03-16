"""Model for fnac product sizes."""

from django.db import models


class Size(models.Model):
    """Model for FNAC sizes."""

    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
